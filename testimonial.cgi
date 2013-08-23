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
require "cgi-bin/vivid.conf";
require "session.pl";
require "common.pl";
#-------------------------------------------------------------------------------

$q = new CGI;
$CGI::HEADERS_ONCE = 1;

#-------------------------------------------------------------------------------
# Database Connection
($dbh) = &getDatabaseConnection();
#-------------------------------------------------------------------------------

&checkSession(refererCheck => 0, postCheck => 0);

print $q->header();
printHeader();
printJSFunctions();

my $action = $q->param('action');
if ($action) {
    my $user_id = $GLOB{user}{user_id};
    my $testimonial = trim($q->param('testimonial'));

    if (!$testimonial) {
        print qq{
            <div class="head" style="text-align:center;">Please enter testimonial.</div>
        };
    }
    else {
        $dbh->do(qq{
            INSERT INTO
                testimonials
                (user_id, testimonial)
            VALUES
                (?, ?)
        }, undef, $user_id, $testimonial);

        print qq{
            <div class="head" style="text-align:center;">Testimonial added successfully.</div>
        };
    }

    print qq{
        <a href="$GLOB{settings}{files_url}/index.cgi">Home</a>
    };
}
else {
    print qq{
        <div class="main_inner_cntnr">
            <div class="main_inner_cntnr_top"></div>
            <div class="main_inner_cntnr_middle">
                <div class="head">Add Testimonials for Vivid Recipes</div>
                <div style="width:300px;position:relative;float:left;margin-top:40px;left:320px;">
                    <form action="" method="post">
                        <textarea name="testimonial" id="testimonial" style="width:300px; height:200px; border:solid 1px #420100;"></textarea>
                        <input type="hidden" name="action" value="add" />
                        <input type="submit" value="Add" onclick="return validateForm();" />
                    </form>
                </div>
            </div>
            <div class="main_inner_cntnr_btm"></div>
        </div>
    };
}

printFooter();

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