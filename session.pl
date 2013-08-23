#-------------------------------------------------------------------------------
# Modules Required
use Digest::MD5;
use CGI::Cookie;
use vars qw($q $dbh %GLOB);
#-------------------------------------------------------------------------------

####----------------------------------------------------------------------------
sub checkSession {
    my %values = @_;

    # Checking if referer is the expected one.
    if ($values{refererCheck} && ($ENV{"SERVER_NAME"} ne $GLOB{settings}{server_name})) {
        &printFatalError("Error!", "Invalid Referer");
    }
    if ($values{postCheck} && ($ENV{"REQUEST_METHOD"} ne 'POST')) {
        &printFatalError("Error!", "Invalid Request method");
    }

    &deleteExpired_SS;

    if (defined $q->param('global_id') && defined $q->param('global_password')) {
        if ($q->param('global_id') =~ /^\s+$/ || $q->param('global_password') =~ /^\s+$/ ) {
            # username/password incorrect.
            &showLoginPage_SS("Incorrect username/password");
            exit;
        }

        if (!$q->param('global_id') || !$q->param('global_password')) {
            # username/password incorrect.
            &showLoginPage_SS("Incorrect username/password");
            exit;
        }

        if (&validUser_SS) {
            # Success.
            &createSession_SS;
        }
        else {
            # username/password incorrect.
            &showLoginPage_SS("Incorrect username/password");
            exit;
        }
    }
    else {
        # Not user login.
        if (&isValidSession_SS) {
            # success
            if ($q->param('logout')) {
                &closeSession_SS;
                &showLoginPage_SS("Logged out");
                exit;
            }
            &refreshSession_SS;
        }
        else {
            # First click/user logged out.
            &showLoginPage_SS("First Click/session timed out");
            exit;
        }
    }
}
####----------------------------------------------------------------------------


####----------------------------------------------------------------------------
sub closeSession_SS {
    # Delete all rows for this session_login_id + user from session table.
    my $row = $dbh->do(qq{
        DELETE FROM
            $GLOB{db}{table}{session}
        WHERE
            user_id = ?
        AND
            session_login_id = ?
    }, undef, $GLOB{user}{$GLOB{db}{field}{id}}, $GLOB{session}{login_id});

    # Print cookies.
    my $cookie_id = new CGI::Cookie(
        -name    => "$GLOB{cookie}{session_id}",
        -value   => "",
        -expires => "-1H",
    );
    my $cookie_login_id = new CGI::Cookie(
        -name    => "$GLOB{cookie}{login_id}",
        -value   => "",
        -expires => "-1H",
    );

    print "Set-Cookie: ", $cookie_id->as_string, "\n";
    print "Set-Cookie: ", $cookie_login_id->as_string, "\n";
}
####----------------------------------------------------------------------------


####----------------------------------------------------------------------------
sub refreshSession_SS {
    # Create new session id.
    $GLOB{session}{id} = &createSessionId_SS;

    # Select all rows for this session_login_id which is over than maxSessionsForLogin - 1.
    my $start = $GLOB{settings}{maxSessionForLogin} - 1;
    my $end = 100;

    my $sth_select_rows = $dbh->prepare(qq{
        SELECT
            row_no
        FROM
            $GLOB{db}{table}{session}
        WHERE
            user_id = ?
        AND
            session_login_id = ?
        ORDER BY
            row_no DESC
        LIMIT
            $start, $end
    });
    $sth_select_rows->execute($GLOB{user}{$GLOB{db}{field}{id}}, $GLOB{session}{login_id});

    my $in_string;
    while (my($db_row_no) = $sth_select_rows->fetchrow_array()) {
        $in_string .= "$db_row_no,";
    }
    $in_string =~ s/,$//;

    # If we got any result for above querry, delete all rows with those row_no.
    if ($in_string) {
        my $row = $dbh->do(qq{
            DELETE FROM
                $GLOB{db}{table}{session}
            WHERE
                row_no IN ($in_string)
        });
    }

    # Insert new session id to new $GLOB{db}{table}{session}.
    $dbh->do(qq{
        INSERT INTO
            $GLOB{db}{table}{session}
            (user_id, session_login_id, session_id, session_time)
        VALUES
            (?, ?, ?, NOW())
    }, undef, $GLOB{user}{$GLOB{db}{field}{id}}, $GLOB{session}{login_id}, $GLOB{session}{id});

    # Print cookies.
    my $cookie_id = new CGI::Cookie(
        -name  => "$GLOB{cookie}{session_id}",
        -value => "$GLOB{session}{id}",
    );
    my $cookie_login_id = new CGI::Cookie(
        -name  => "$GLOB{cookie}{login_id}",
        -value => "$GLOB{session}{login_id}",
    );

    print "Set-Cookie: ", $cookie_id->as_string, "\n";
    print "Set-Cookie: ", $cookie_login_id->as_string, "\n";

    return 1;
}
####----------------------------------------------------------------------------


####----------------------------------------------------------------------------
sub isValidSession_SS {
    my $old_session_id = $q->cookie($GLOB{cookie}{session_id}) || $q->param($GLOB{cookie}{session_id});
    my $old_session_login_id = $q->cookie($GLOB{cookie}{login_id}) || $q->param($GLOB{cookie}{login_id});

    if (!$old_session_id || !$old_session_login_id) {
        # Logging in for first time, or cookie got deleted/expired.
        return 0;
    }

    my $sth_session_ids=$dbh->prepare(qq{
        SELECT
            user_id, session_id
        FROM
            $GLOB{db}{table}{session}
        WHERE
            session_login_id = ?
        ORDER BY
            row_no DESC
        LIMIT
            $GLOB{settings}{maxSessionForLogin}
    });
    $sth_session_ids->execute($old_session_login_id);

    my %temp_sessions;
    while (my($db_user, $db_sessionid) = $sth_session_ids->fetchrow_array()) {
        $temp_sessions{$db_sessionid} = $db_user;
    }

    if (exists $temp_sessions{$old_session_id}) {
        $GLOB{session}{login_id} = $old_session_login_id;

        my $sth_select_user = $dbh->prepare(qq{
            SELECT
                *
            FROM
                $GLOB{db}{table}{user_profile}
            WHERE
                $GLOB{db}{field}{id} = ?
        });
        $sth_select_user->execute($temp_sessions{$old_session_id});

        my %data;
        $sth_select_user->bind_columns( \( @data{ @{$sth_select_user->{NAME_lc} } } ));
        $sth_select_user->fetchrow_hashref;
        foreach my $item (keys %data) {
            $GLOB{user}{$item} = $data{$item};
        }

        $GLOB{user}{$GLOB{db}{field}{id}} = lc($GLOB{user}{$GLOB{db}{field}{id}});

        return 1;
    }
    else {
        return 0;
    }
}
####----------------------------------------------------------------------------


####----------------------------------------------------------------------------
sub deleteExpired_SS {
    # Here we will delete all those session rows which is older than timeToLive.
    # We are giving this as a low priority delete so that selects are given priority.
    # session_time field is not given a index(neither btree, nor heap) because
    # this querry wont use indexing, as its now()-session_time, mysql need to do this
    # calculation for all rows.

    my $row = $dbh->do(qq{
        DELETE LOW_PRIORITY FROM
            $GLOB{db}{table}{session}
        WHERE
            UNIX_TIMESTAMP(NOW()) - UNIX_TIMESTAMP(session_time) > ?
    }, undef, $GLOB{settings}{timeToLive});
}
####----------------------------------------------------------------------------


####----------------------------------------------------------------------------
# Create new session
sub createSession_SS {
    # Select all session login ids for this user which is over the assigned limit.
    my $start = 15;# $GLOB{user}{usr_max_sessions} - 1;
    my $end = 100;

    my $sth_session_ids = $dbh->prepare(qq{
        SELECT
            session_login_id
        FROM
            $GLOB{db}{table}{session}
        WHERE
            user_id = ?
        ORDER BY
            row_no DESC
        LIMIT
            100, 1
    });
    $sth_session_ids->execute($GLOB{user}{$GLOB{db}{field}{id}});
    my $in_string;
    while (my($db_session_login_id) = $sth_session_ids->fetchrow_array()) {
        $in_string .= "$db_session_login_id,";
    }
    $in_string =~ s/,$//;

    # If we got any result for above querry, delete all rows with those login_session_ids.
    if ($in_string) {
        my $row = $dbh->do(qq{
            DELETE FROM
                $GLOB{db}{table}{session}
            WHERE
                session_login_id IN ($in_string)
        });
    }

    # Now we got space for new session_login_id, so create new session login id.
    # Create session Login Id
    $dbh->{AutoCommit} = 0;
    $dbh->do(qq{
        UPDATE
            $GLOB{db}{table}{session_id}
        SET
            value_field = value_field + 1
        WHERE
            key_field = 'session_login_id'
    });

    ($GLOB{session}{login_id}) = $dbh->selectrow_array(qq{
        SELECT
            value_field
        FROM
            $GLOB{db}{table}{session_id}
        WHERE
            key_field = 'session_login_id'
    });

    $dbh->commit;
    $dbh->{AutoCommit} = 1;

    # Now, create new session id.
    $GLOB{session}{id} = &createSessionId_SS;

    # Insert to session table.
    $dbh->do(qq{
        INSERT INTO
            $GLOB{db}{table}{session}
            (user_id, session_login_id, session_id, session_time)
        VALUES
            (?, ?, ?, NOW())
    }, undef, $GLOB{user}{$GLOB{db}{field}{id}}, $GLOB{session}{login_id}, $GLOB{session}{id});

    # Print cookies.
    my $cookie_id = new CGI::Cookie(
        -name  => "$GLOB{cookie}{session_id}",
        -value => "$GLOB{session}{id}",
    );
    my $cookie_login_id = new CGI::Cookie(
        -name  => "$GLOB{cookie}{login_id}",
        -value => "$GLOB{session}{login_id}",
    );

    print "Set-Cookie: ", $cookie_id->as_string, "\n";
    print "Set-Cookie: ", $cookie_login_id->as_string, "\n";

    return 1;
}
####----------------------------------------------------------------------------


####----------------------------------------------------------------------------
sub createSessionId_SS {
    my $id = "";
    my @chars = ("a".."z", "A".."Z", 0..9);
    my $x;
    for ($x = 0; $x < 14; $x++) {
        $id .= $chars[int(rand(62))];
    }
    my $sessionID = Digest::MD5::md5_hex($$.time().$id);
    return $sessionID;
}
####----------------------------------------------------------------------------


####----------------------------------------------------------------------------
# To check if the username/password entered by user is valid or not!
# If it valid, the hash $GLOB{user} will be loaded with user settings.
sub validUser_SS {
    my $sth_select_user = $dbh->prepare(qq{
        SELECT
            *
        FROM
            $GLOB{db}{table}{user_profile}
        WHERE
            $GLOB{db}{field}{user_name} = ?
        AND
            $GLOB{db}{field}{password} = ?
    });
    $sth_select_user->execute($q->param('global_id'), $q->param('global_password'));

    my %data;
    $sth_select_user->bind_columns( \( @data{ @{$sth_select_user->{NAME_lc} } } ));
    $sth_select_user->fetchrow_hashref;

    foreach my $item (keys %data) {
        $GLOB{user}{$item} = $data{$item};
    }

    $GLOB{user}{$GLOB{db}{field}{id}} = lc($GLOB{user}{$GLOB{db}{field}{id}});

    if ($GLOB{user}{$GLOB{db}{field}{id}}) {
        return 1;
    }
    else {
        # Faield to authenticate user.
        # Increment user_failed counter.
        return 0;
    }
}
####----------------------------------------------------------------------------


####----------------------------------------------------------------------------
# Showing login page.
sub showLoginPage_SS {
    my ($message) = @_;
    print $q->redirect("$GLOB{settings}{files_url}/index.cgi");
}
#-----------------------------PROGRAM ENDS------------------------------------##

1;