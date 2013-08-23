#!/usr/bin/perl

#-------------------------------------------------------------------------------
# Modules Required
use CGI;
use CGI::Carp qw(fatalsToBrowser);
use strict;
use vars qw(%GLOB $q $dbh);
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
# Libraries Required
require "../cgi-bin/vivid.conf";
require "../session.pl";
require "../common.pl";
#-------------------------------------------------------------------------------

$q = new CGI;
$CGI::HEADERS_ONCE = 1;

#-------------------------------------------------------------------------------
# Database Connection
($dbh) = &getDatabaseConnection();
#-------------------------------------------------------------------------------

&checkSession(refererCheck => 0, postCheck => 0);
my $email = $GLOB{user}{email};
print $q->redirect("$GLOB{settings}{files_url}/index.cgi") if ($email ne 'admin');

print $q->header();
printHeader();
printJSFunctions();

print qq{
    <div class="main_inner_cntnr">
        <div class="main_inner_cntnr_top"></div>
        <div class="main_inner_cntnr_middle">
            <div class="head">Testimonials</div>
            <div class="admin_cntnr">
};

my $action = $q->param('action');
my $testimonial_id = $q->param('id');

if ($action && !$testimonial_id) {
    print qq{
        No testimonial selected.
    };
}
elsif ($action eq 'view') {
    viewTestimonial();
}
elsif ($action eq 'edit') {
    editTestimonial();
}
elsif ($action eq 'update') {
    updateTestimonial();
}
elsif ($action eq 'delete') {
    deleteTestimonial();
}
else {
    listTestimonials();
}

print qq{
            </div>
        </div>
        <div class="main_inner_cntnr_btm"></div>
    </div>
};

printFooter();

sub listTestimonials {
    my $sth = $dbh->prepare(qq{
        SELECT
            SQL_CALC_FOUND_ROWS
            a.testimonial_id,
            a.testimonial,
            DATE_FORMAT(a.added_date, '%d-%m-%Y') AS added_date,
            b.name
        FROM
            testimonials AS a,
            users AS b
        WHERE
            a.user_id = b.user_id
        ORDER BY
            added_date DESC,
            a.testimonial
    });
    $sth->execute;
    my ($result) = $dbh->selectrow_array(qq{SELECT FOUND_ROWS()});
    if ($result) {
        print qq{
            <div style="position:relative; float:left; width:100%;">
                <div style="position:relative; float:left; width:5%;"><b>#</b></div>
                <div style="position:relative; float:left; width:20%;"><b>User Name</b></div>
                <div style="position:relative; float:left; width:20%;"><b>Testimonial</b></div>
                <div style="position:relative; float:left; width:20%;"><b>Added Date</b></div>
            </div>
        };

        my $count = 0;
        while (my ($testimonial_id, $testimonial, $added_date, $name) = $sth->fetchrow_array) {
            $count++;
            my $class_name = ($count % 2 == 0) ? 'even' : 'odd';
            $testimonial = substr($testimonial, 0, 10) . '...' if (length($testimonial) > 10);

            print qq{
                <div class="$class_name" style="position:relative; float:left; width:100%;">
                    <div style="position:relative; float:left; width:5%;">$count</div>
                    <div style="position:relative; float:left; width:20%;">$name</div>
                    <div style="position:relative; float:left; width:20%;">$testimonial</div>
                    <div style="position:relative; float:left; width:20%;">$added_date</div>
                    <div style="position:relative; float:left; width:10%;">
                        <a href="?action=view&id=$testimonial_id"><input type="button" value="View" /></a>
                    </div>
                    <div style="position:relative; float:left; width:10%;">
                        <a href="?action=edit&id=$testimonial_id"><input type="button" value="Edit" /></a>
                    </div>
                    <div style="position:relative; float:left; width:10%;">
                        <a href="?action=delete&id=$testimonial_id"><input type="button" value="Delete" onclick="if (confirm('Are you sure you want to delete this testimonial?') == false) return false;" /></a>
                    </div>
                </div>
            };
        }
    }
    else {
        print qq{
            No testimonials
            <a href="$GLOB{settings}{files_url}/admin/index.cgi">Back</a>
        };
    }
}

sub viewTestimonial {
    my ($testimonial_id, $testimonial) = $dbh->selectrow_array(qq{
        SELECT
            testimonial_id,
            testimonial
        FROM
            testimonials
        WHERE
            testimonial_id = ?
    }, undef, $testimonial_id);

    if (!$testimonial_id) {
        print qq{
            This testimonial does not exist.
        };
    }
    else {
        $testimonial =~ s/\r\n|\r|\n/<br>/g;

        print qq{
            <div>$testimonial</div>
        };
    }

    print qq{
        <a href="$GLOB{settings}{files_url}/admin/testimonials.cgi">Back</a>
    };
}

sub editTestimonial {
    my ($testimonial_id, $testimonial) = $dbh->selectrow_array(qq{
        SELECT
            testimonial_id,
            testimonial
        FROM
            testimonials
        WHERE
            testimonial_id = ?
    }, undef, $testimonial_id);

    if (!$testimonial_id) {
        print qq{
            This testimonial does not exist.
        };
    }
    else {
        print qq{
            <form action="" method="post">
                <textarea name="testimonial" id="testimonial" style="width:300px; height:200px; border:solid 1px #420100;">$testimonial</textarea>
                <input type="hidden" name="id" value="$testimonial_id" />
                <input type="hidden" name="action" value="update" />
                <input type="submit" value="Update" onclick="return validateForm();" />
            </form>
        };
    }

    print qq{
        <a href="$GLOB{settings}{files_url}/admin/testimonials.cgi">Back</a>
    };
}

sub updateTestimonial {
    my ($testimonial_id) = $dbh->selectrow_array(qq{
        SELECT
            testimonial_id
        FROM
            testimonials
        WHERE
            testimonial_id = ?
    }, undef, $testimonial_id);
    my $testimonial = trim($q->param('testimonial'));

    if (!$testimonial_id) {
        print qq{
            This testimonial does not exist.
        };
    }
    elsif (!$testimonial) {
        print qq{
            Please enter testimonial.
        };
    }
    else {
        $dbh->do(qq{
            UPDATE
                testimonials
            SET
                testimonial = ?
            WHERE
                testimonial_id = ?
        }, undef, $testimonial, $testimonial_id);

        print qq{
            Testimonial updated successfully.
        };
    }

    print qq{
        <a href="$GLOB{settings}{files_url}/admin/testimonials.cgi">Back</a>
    };
}

sub deleteTestimonial {
    my ($testimonial_id) = $dbh->selectrow_array(qq{
        SELECT
            testimonial_id
        FROM
            testimonials
        WHERE
            testimonial_id = ?
    }, undef, $testimonial_id);

    if (!$testimonial_id) {
        print qq{
            This testimonial does not exist.
        };
    }
    else {
        $dbh->do(qq{
            DELETE FROM
                testimonials
            WHERE
                testimonial_id = ?
        }, undef, $testimonial_id);

        print qq{
            Testimonial deleted successfully.
        };
    }

    print qq{
        <a href="$GLOB{settings}{files_url}/admin/testimonials.cgi">Back</a>
    };
}

sub printJSFunctions {
    print qq{
        <script type="text/javascript">
            function validateForm() {
                var testimonial = document.getElementById('testimonial').value;

                if (testimonial == '' || testimonial == null) {
                    alert('Please enter testimonial');
                    document.getElementById('testimonial').focus();
                    return false;
                }

                return true;
            }
        </script>
    };
}