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
($dbh) = &getDatabaseConnection();
#-------------------------------------------------------------------------------

print $q->header();
printHeader();

my $sth = $dbh->prepare(qq{
    SELECT
        recipe_id,
        name
    FROM
        recipes
    WHERE
        top_ten_recipe = 1
    ORDER BY
        name
    LIMIT 10
});
$sth->execute;
while (my ($recipe_id, $name) = $sth->fetchrow_array) {
    print qq{
        <a href="item.cgi?recipe_id=$recipe_id">$name</a>
    };
}

printFooter();