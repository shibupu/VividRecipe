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

if (isValidSession_SS()) {
    print $q->redirect('index.cgi');
}

print $q->header();
printHeader();
printJSFunctions();

print qq{
    <div class="main_inner_cntnr">
        <div class="main_inner_cntnr_top"></div>
        <div class="main_inner_cntnr_middle">
};

if ($q->param('action')) {
    my $email = trim($q->param('email'));
    my $password = trim($q->param('password'));
    my $name = trim($q->param('name'));
    my $address = trim($q->param('address'));
    my $place = trim($q->param('place'));
    my $city = trim($q->param('city'));
    my $state = trim($q->param('state'));
    my $pin = trim($q->param('pin'));
    my $phone = trim($q->param('phone'));

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
    elsif (duplicateEmail($email)) {
        print 'Your e-mail address is already registered with us.';
    }
    elsif (!$password) {
        print 'Please enter password.';
    }
    else {
        $dbh->do(qq{
            INSERT INTO
                users
                (email, password, name, address, place, city, state, pin, phone)
            VALUES
                (?, ?, ?, ?, ?, ?, ?, ?, ?)
        }, undef, $email, $password, $name, $address, $place, $city, $state, $pin, $phone);

        my $subject = 'Registration Successful';
        my $body = "Hi $name,\n\nYou are successfully registered with Vivid Recipe.\n\nUsername: $email\nPassword: $password\n";
        my $mail_sent_status = sendMail($email, $subject, $body);

        print 'You are registered successfully.';
    }

    print '</div>';
}
else {
    print qq{
            <div class="head">Signup With Vivid Recipe</div>
            <form action="" method="post">
                <div class="signupdatacntnr">
                    <div class="inner">
                        <div class="tp">
                            <div>Name:</div>
                            <div><input type="text" name="name" id="name" /></div>
                        </div>
                        <div class="tp">
                            <div>Email:</div>
                            <div><input type="text" name="email" id="email" /></div>
                        </div>
                        <div class="tp">
                            <div>Place:</div>
                            <div><input type="text" name="place" /></div>
                        </div>
                        <div class="tp">
                            <div>State:</div>
                            <div><input type="text" name="state" /></div>
                        </div>
                        <div class="tp">
                            <div>Phone:</div>
                            <div><input type="text" name="phone" /></div>
                        </div>
                    </div>
                    <div class="inner">
                        <div class="tp">
                            <div>Address:</div>
                            <div><input type="text" name="address" /></div>
                        </div>
                        <div class="tp">
                            <div>Password:</div>
                            <div><input type="password" name="password" id="password" /></div>
                        </div>
                        <div class="tp">
                            <div>City:</div>
                            <div><input type="text" name="city" /></div>
                        </div>
                        <div class="tp">
                            <div>PIN:</div>
                            <div><input type="text" name="pin" /></div>
                        </div>
                        <div class="tp">
                            <div style="width:80px; left:135px; margin-bottom:20px;">
                                <input type="hidden" name="action" value="Register" />
                                <input type="submit" value="Register" onclick="return validateForm();" style="background-color:#420100; color:#fff; cursor:pointer;" />
                            </div>
                        </div>
                    </div>
                </div>
            </form>
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
                var name = document.getElementById('name').value;
                var email = document.getElementById('email').value;
                var password = document.getElementById('password').value;

                if (name == '' || name == null) {
                    alert('Please enter name');
                    document.getElementById('name').focus();
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

                if (password == '' || password == null) {
                    alert('Please enter password');
                    document.getElementById('password').focus();
                    return false;
                }

                return true;
            }
        </script>
    };
}