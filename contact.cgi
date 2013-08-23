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
require "common.pl";
require "session.pl";
#-------------------------------------------------------------------------------

$q = new CGI;
$CGI::HEADERS_ONCE = 1;

#-------------------------------------------------------------------------------
# Database Connection
($dbh) = getDatabaseConnection();
#-------------------------------------------------------------------------------

print $q->header();
printHeader();
printJSFunctions();

print qq{
    <div class="main_inner_cntnr">
        <div class="main_inner_cntnr_top"></div>
        <div class="main_inner_cntnr_middle">
};

if ($q->param('action')) {
    my $name = trim($q->param('full_name'));
    my $email = trim($q->param('email'));
    my $place = trim($q->param('place'));
    my $phone = trim($q->param('phone'));
    my $subject = trim($q->param('subject'));
    my $comment = trim($q->param('comment'));

    print qq{<div class="head" style="text-align:center;">};

    if (!$name) {
        print 'Please enter name.';
    }
    elsif (!$email) {
        print 'Please enter email address.';
    }
    elsif (invalidEmail($email)) {
        print 'Please enter valid email address.';
    }
    elsif (!$comment) {
        print 'Please enter comment/question.';
    }
    else {
        my $body = "Name: $name\n\nEmail: $email\n\nPlace: $place\n\nPhone: $phone\n\nSubject: $subject\n\nComment/Question:\n$comment";
        $subject ||= 'Vivid Recipe Contact Form';
        my $mail_sent_status = sendMail($GLOB{smtp}{username}, $subject, $body);
        if ($mail_sent_status == 1) {
            print 'Your comment/question is sent successfully. Thank you for contacting us.';
        }
        else {
            print 'Sorry!!! An error occured. Please try again later.';
        }
    }

    print '</div>';
}
else {
    print qq{
            <div class="head">Contact Us</div>
            <div class="contact_data3">
                <form action="" method="post">
                    <div class="contact_inner">
                        <div class="contact_data_inner">
                            <div class="contact_data_frmt">Name</div>
                            <div><input type="text" name="full_name" id="full_name" class="input" /></div>
                        </div>
                        <div class="contact_data_inner">
                            <div class="contact_data_frmt">Email</div>
                            <div><input type="text" name="email" id="email" class="input" /></div>
                        </div>
                        <div class="contact_data_inner">
                            <div class="contact_data_frmt">Place</div>
                            <div><input type="text" name="place" class="input" /></div>
                        </div>
                        <div class="contact_data_inner">
                            <div class="contact_data_frmt">Phone</div>
                            <div><input type="text" name="phone" class="input" /></div>
                        </div>
                    </div>
                    <div class="contact_inner">
                        <div class="contact_data_inner">
                            <div class="contact_data_frmt">Subject</div>
                            <div><input type="text" name="subject" class="input" /></div>
                        </div>
                        <div class="contact_data_inner">
                            <div class="contact_data_frmt">Comment/Question</div>
                            <div><textarea name="comment" id="comment" class="input" style="height:100px;"></textarea></div>
                        </div>
                        <div class="contact_data_inner" style="top:20px; text-align:center;">
                            <input type="image" src="$GLOB{settings}{files_url}/images/submit.gif" onclick="return validateForm();" />
                            <input type="hidden" name="action" value="Submit" />
                        </div>
                    </div>
                </form>
            </div>
    };
}

print qq{
        </div>
        <div class="main_inner_cntnr_btm"></div>
    </div>
};

printFooter();

sub printJSFunctions {
    print qq{
        <script type="text/javascript">
            function validateForm() {
                var full_name = document.getElementById('full_name').value;
                var email = document.getElementById('email').value;
                var comment = document.getElementById('comment').value;

                if (full_name == '' || full_name == null) {
                    alert('Please enter name');
                    document.getElementById('full_name').focus();
                    return false;
                }

                if (email == '' || email == null) {
                    alert('Please enter email address');
                    document.getElementById('email').focus();
                    return false;
                }

                if (email) {
                    atpos = email.indexOf("@");
                    dotpos = email.lastIndexOf(".");
                    if (atpos < 1 || dotpos - atpos < 2) {
                        alert('Please enter valid email address.');
                        document.getElementById('email').focus();
                        return false;
                    }
                }

                if (comment == '' || comment == null) {
                    alert('Please enter comment/question');
                    document.getElementById('comment').focus();
                    return false;
                }

                return true;
            }
        </script>
    };
}