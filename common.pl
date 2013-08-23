#-------------------------------------------------------------------------------
#Modules Required
use DBI;
use strict;
use vars qw(%GLOB $dbh $q);
#-------------------------------------------------------------------------------

sub getDatabaseConnection {
    my $extra .= "host=$GLOB{db}{hostname};" if $GLOB{db}{hostname};
    $extra .= "port=$GLOB{db}{port};" if $GLOB{db}{port};
    my $temp_dbh = DBI->connect("DBI:mysql:database=$GLOB{db}{name};$extra", $GLOB{db}{username}, $GLOB{db}{password}, {AutoCommit => 1});
    if (!$temp_dbh) {
        &printFatalError('Database Connection Error', 'Database Connection Failed.');
    }
    $temp_dbh->{HandleError} = sub {
        &printFatalError('Database Error', 'Database Operation Failed.');
    };

    return ($temp_dbh);
}

sub printFatalError {
    my ($heading, $message) = @_;

    if (defined $q) {
        print $q->header();

        print qq{
            <div style="position:absolute; width:60%; left:20%; border:solid 1px red; float:left; top:250px; background-color:#FFEBE8;">
                <div>
                    <br/>
                    <div style="position:relative; float:left; left:4%; font-family:verdana; font-size:25px; font-weight:900; color:#ff0000;">$heading</div>
                    <br/><br/>
                    <div style="position:relative; float:left; left:4%; font-family:verdana; font-size:13px; font-weight:600; color:#000000;">$message</div>
                    <br/><br/>
                </div>
            </div>
        };
    }
    else {
        print "$heading: $message\n";
    }

    exit;
}

sub printHeader {
    my $keyword = trim($q->param('keyword')) || '-Search Recipes-';

    print qq{
        <?xml version="1.0" encoding="UTF-8"?>
        <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
        <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
            <head>
                <title>Vivid Recipe</title>
                <meta name="keywords" content="Free Indian Recipes, Indian Veg Recipes, Indian Cooking Recipes, Non Veg Recipes, Vegetarian Dishes, Recipes For Cooking, Recipe Videos, Recipe Gallery, Recipe Photos" />
                <meta name="description" content="Vivid Recipe – offers Thousands of Indian Recipes, Recipe Videos, Photos, Expert Recipes. Get free Indian Cooking Recipes and share your Faourite food recipe." />
                <link rel="stylesheet" type="text/css" href="$GLOB{settings}{files_url}/css/vivid.css" />
                <script type="text/javascript" src="$GLOB{settings}{files_url}/js/swfobject/swfobject.js"></script>
                <script type="text/javascript">
                    var login = 0;
                    var flashvars = {};
                    flashvars.xml = "config.xml";
                    flashvars.font = "font.swf";
                    var attributes = {};
                    attributes.wmode = "transparent";
                    attributes.id = "slider";
                    swfobject.embedSWF("cu3er.swf", "cu3er-container", "474", "267", "9", "expressInstall.swf", flashvars, attributes);
                </script>
                <script type="text/javascript">
                    var _gaq = _gaq || [];
                    _gaq.push(['_setAccount', 'UA-21606945-1']);
                    _gaq.push(['_trackPageview']);

                    (function() {
                        var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
                        ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
                        var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
                    })();
                  </script>
            </head>
            <body>
                <div class="main_cntnr">

                    <div class="top_menu">
                        <div class="inner"><a href="$GLOB{settings}{files_url}/index.cgi">Home</a></div>
                        <div class="inner"><a href="$GLOB{settings}{files_url}/about.cgi">About</a></div>
                        <div class="inner"><a href="$GLOB{settings}{files_url}/recipes.cgi">Recipes</a></div>
                        <div class="inner"><a href="$GLOB{settings}{files_url}/recipe.cgi" onclick="if (!login) {alert('You should login to submit a recipe'); return false;}">Submit A Recipe</a></div>
                        <div class="inner"><a href="$GLOB{settings}{files_url}/top_videos.cgi">Top Videos</a></div>
                        <div class="inner"><a href="$GLOB{settings}{files_url}/contact.cgi">Contact</a></div>
                    </div>

                    <div class="logo_cntnr">
                        <div class="logo"><img src="$GLOB{settings}{files_url}/images/logo.png" alt="" /></div>
                        <div class="search">
                            <form action="$GLOB{settings}{files_url}/recipes.cgi" method="post">
                                <input type="text" name="keyword" value="$keyword" class="keyword" onclick="if (this.value == '-Search Recipes-') this.value = '';" onblur="if (this.value == '') this.value = '-Search Recipes-';" />
                                <input type="image" src="$GLOB{settings}{files_url}/images/serch_icon.png" class="lens" />
                            </form>
                        </div>

                        <div class="login_cntnr">
    };

    if (isValidSession_SS()) {
        print qq{
                            <script type="text/javascript">login = 1;</script>
                            <div class="welcome">Welcome $GLOB{user}{name}!</div>
                            <a href="$GLOB{settings}{files_url}/testimonial.cgi"><img src="$GLOB{settings}{files_url}/images/add_testimonial.png" style="border:none;" /></a>
                            <a href="$GLOB{settings}{files_url}/recipe.cgi"><img src="$GLOB{settings}{files_url}/images/add_recipes.png" style="border:none;" /></a>
                            <a href="$GLOB{settings}{files_url}/login.cgi?logout=1"><img src="$GLOB{settings}{files_url}/images/logout.png" style="border:none;" /></a>
        };
    }
    else {
        print qq{
                            <div class="signup"><a href="$GLOB{settings}{files_url}/signup.cgi"><img src="$GLOB{settings}{files_url}/images/signup.png" alt="" style="border:none;" /></a></div>
                            <div class="login_bg">
                                <div class="inner_cntnr">
                                    <form action="login.cgi" method="post">
                                        <div class="input_cntnr">
                                            <input type="text" name="global_id" />
                                            <input type="password" name="global_password" />
                                        </div>
                                        <div class="go"><input type="image" src="$GLOB{settings}{files_url}/images/go.png" /></div>
                                    </form>
                                </div>
                            </div>
        };
    }

    print qq{
                        </div>
                    </div>
    };
}

sub printFooter {
    print qq{
                </div>
            </body>
        </html>
    };
}

sub duplicateEmail {
    my ($mail) = @_;
    return $dbh->selectrow_array(qq{
        SELECT
            COUNT(*)
        FROM
            users
        WHERE
            email = ?
    }, undef, $mail);
}

sub invalidEmail {
    my ($email) = @_;
    return ($email =~ /^(\w|\-|\.)+\@(\w|\-)+\.[a-zA-Z\.]{2,}$/) ? 0 : 1;
}

sub trim {
    my $string = shift;
    $string =~ s/^\s+//;
    $string =~ s/\s+$//;
    return $string;
}

sub sendMail {
    my ($to, $subject, $body) = @_;
    my $from = "Vivid Recipe<$GLOB{smtp}{username}>";

    use Net::SMTP::SSL;
    my $smtp = Net::SMTP::SSL->new(
        $GLOB{smtp}{host},
        Port => $GLOB{smtp}{port},
        Debug => 1
    );

    if (!$smtp) {
        #print "Couldn't connect to server!<br>";
        return -1;
    }

    if (!$smtp->auth($GLOB{smtp}{username}, $GLOB{smtp}{password})) {
        #print "Authentication failed!<br>";
        return -2;
    };

    $smtp->mail($from . "\n");
    $smtp->to($to . "\n");
    $smtp->data();
    $smtp->datasend("From: " . $from . "\n");
    $smtp->datasend("To: " . $to . "\n");
    $smtp->datasend("Subject: " . $subject . "\n");
    $smtp->datasend("\n");
    $smtp->datasend($body . "\n");
    $smtp->dataend();
    $smtp->quit;

    return 1;
}

sub pagination {
    my ($total_results, $default_url, $results_per_page) = @_;

    # get the input params
    my $offset        = $q->param('offset') || 0;
    my $left_padding  = 3;
    my $right_padding = 3;
    my $row_start     = $offset * $results_per_page;
    my $row_end       = $row_start + $results_per_page;
    my $result;

    if ($row_end > $total_results) {
        $row_end = $total_results;
    }

    # Pagination structure
    # << Previous - 1 - 2 - 3 - 4 - 5 - 6 - 7 - Next >>
    my $total_mod = $total_results % $results_per_page;
    my $tot_pg = $total_results / $results_per_page;
    my $totalPages;
    if ($tot_pg < 1) {
        $totalPages = int($total_results / $results_per_page);
    }
    else {
        $totalPages = (!$total_mod) ? int($total_results / $results_per_page) : int($total_results / $results_per_page) + 1;
    }

    return unless ($totalPages);

    my $leftPad = $offset - 3;
    my $rightPad = $offset + 3;
    if ($leftPad < 0) {
        $leftPad = 0;
        $rightPad = 6;
    }
    if ($rightPad > $totalPages) {
        $rightPad = $totalPages;
    }

    # Display the Previous button
    if ($offset != 0) {
        $result .= qq{
            <div class="pgnt_btn_cntnr">
                <a href=${default_url}offset=0>
                    <img src="$GLOB{settings}{files_url}/images/start.gif" border="0" />
                </a>
            </div>
            <div class="pgnt_btn_cntnr" style="margin-right: 5px;">
                <a href=${default_url}offset=} . ($offset - 1) . qq{>
                    <img src="$GLOB{settings}{files_url}/images/previous.gif" border="0" />
                </a>
            </div>
        };
    }

    # Dispaly the Pagination
    if ($totalPages > 1) {
        my $x;
        for ($x = $leftPad; $x < $rightPad; $x++) {
            if ($x == $offset) {
                if ($x == $rightPad) {
                    $result .= qq{<div class="pgnt_num_cntnr" style="color:#959595;">} . ($x + 1) . qq{</div>};
                }
                else {
                    $result .= qq{<div class="pgnt_num_cntnr" style="color:#959595;">} . ($x + 1) . qq{</div>};
                }
            }
            else {
                $result .= qq{<a href=${default_url}offset=$x><div class="pgnt_num_cntnr">} . ($x + 1) . qq{</div></a>};
            }
        }
    }

    # Display the Next button
    if ((($offset * $results_per_page) + $results_per_page) < $total_results) {
        my $last_offset = $totalPages - 1;
        $result .= qq{
            <div class="pgnt_btn_cntnr" style="margin-left: 5px;">
                <a href=${default_url}offset=} . ($offset + 1) . qq{>
                    <img src="$GLOB{settings}{files_url}/images/next.gif" border="0" />
                </a>
            </div>
            <div class="pgnt_btn_cntnr">
                <a href=${default_url}offset=$last_offset>
                    <img src="$GLOB{settings}{files_url}/images/end.gif" border="0" />
                </a>
            </div>
        };
    }

    # Output all in format
    print qq{
        <div class="pgnt_cntnr">$result</div>
    };
}

1;