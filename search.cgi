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

my $top = $q->param('top');
my $easy = $q->param('easy');
my $style = $q->param('style');
my $category = $q->param('category');
my $keyword = trim($q->param('keyword'));
$keyword = '' if ($keyword eq '-Search Recipes-');

my $sth;

if ($top) {
    $sth = $dbh->prepare(qq{
        SELECT
            SQL_CALC_FOUND_ROWS
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
}
elsif ($easy) {
    $sth = $dbh->prepare(qq{
        SELECT
            SQL_CALC_FOUND_ROWS
            recipe_id,
            name
        FROM
            recipes
        WHERE
            easy_recipe = 1
        ORDER BY
            name
    });
    $sth->execute;
}
elsif ($style) {
    $sth = $dbh->prepare(qq{
        SELECT
            SQL_CALC_FOUND_ROWS
            recipe_id,
            name
        FROM
            recipes
        WHERE
            style = ?
        ORDER BY
            name
    });
    $sth->execute($style);
}
elsif ($category) {
    $sth = $dbh->prepare(qq{
        SELECT
            SQL_CALC_FOUND_ROWS
            recipe_id,
            name
        FROM
            recipes
        WHERE
            category = ?
        ORDER BY
            name
    });
    $sth->execute($category);
}
elsif ($keyword) {
    $sth = $dbh->prepare(qq{
        SELECT
            SQL_CALC_FOUND_ROWS
            recipe_id,
            name
        FROM
            recipes
        WHERE
            name LIKE ?
        OR
            description LIKE ?
        OR
            ingredients LIKE ?
        ORDER BY
            name
    });
    $sth->execute("%$keyword%", "%$keyword%", "%$keyword%");
}
else {
    $sth = $dbh->prepare(qq{
        SELECT
            SQL_CALC_FOUND_ROWS
            recipe_id,
            name
        FROM
            recipes
        ORDER BY
            name
    });
    $sth->execute;
}

print qq{
    <div class="main_inner_cntnr">
        <div class="main_inner_cntnr_top"></div>
        <div class="main_inner_cntnr_middle">
            <div class="head"></div>
};

my ($result) = $dbh->selectrow_array(qq{SELECT FOUND_ROWS()});
if ($result) {
    print qq{
            <div class="search_result_cntnr">
    };

    while (my ($recipe_id, $name) = $sth->fetchrow_array) {
        print qq{
                <div class="search_result_cntnr_inner" style="width:100%;">
                    <a href="$GLOB{settings}{files_url}/item.cgi?recipe_id=$recipe_id">$name</a>
                </div>
        };
    }

    print qq{
            </div>
    };
}
else {
    print qq{
        No recipes found in the search.
    };
}

print qq{
        </div>
        <div class="main_inner_cntnr_btm"></div>
    </div>
};

printFooter();