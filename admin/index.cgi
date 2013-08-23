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

print qq{
    <div class="main_inner_cntnr">
        <div class="main_inner_cntnr_top"></div>
        <div class="main_inner_cntnr_middle">
            <div class="head">Signup With Vivid Recipes</div>
};

print qq{
            <div class="admin_cntnr">
                <a href="$GLOB{settings}{files_url}/admin/top_ten_recipes.cgi">Top 10 Recipes</a>
                <a href="$GLOB{settings}{files_url}/admin/todays_recipe.cgi">Dish of the Day</a>
                <a href="$GLOB{settings}{files_url}/admin/easy_recipes.cgi">Easy Recipes</a>
                <a href="$GLOB{settings}{files_url}/admin/testimonials.cgi">Testimonials</a>
                <a href="$GLOB{settings}{files_url}/admin/recipes.cgi">All Recipes</a>
            </div>
};


print qq{
        </div>
        <div class="main_inner_cntnr_btm"></div>
    </div>
};

printFooter();