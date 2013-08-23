#!/usr/bin/perl

#-------------------------------------------------------------------------------
# Modules Required
use CGI;
use CGI::Carp qw(fatalsToBrowser);
use URI::Escape;
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

my ($cond, $limit);
my $top = $q->param('top');
my $easy = $q->param('easy');
my $style = $q->param('style');
my $category = $q->param('category');
my $keyword = trim($q->param('keyword'));
$keyword = '' if ($keyword eq '-Search Recipes-');
my $default_url = "$GLOB{settings}{files_url}/recipes.cgi?";

if ($top) {
    $cond = 'a.top_ten_recipe = 1';
    $limit = 'LIMIT 10';
    $default_url .= "top=$top";
}
elsif ($easy) {
    $cond = 'a.easy_recipe = 1';
    $default_url .= "easy=$easy";
}
elsif ($style) {
    $cond = "FIND_IN_SET('$style', a.style)";
    $default_url .= "style=$style";
}
elsif ($category) {
    $cond = "FIND_IN_SET('$category', a.category)";
    $default_url .= "category=$category";
}
elsif ($keyword) {
    $keyword =~ s/'/\\'/g;
    $keyword =~ s/%/\\%/g;
    $cond = "(a.name LIKE '%$keyword%' OR a.description LIKE '%$keyword%' OR a.ingredients LIKE '%$keyword%')";
    $default_url .= 'keyword=' . uri_escape($keyword);
}

$cond = "AND $cond" if ($cond);

print qq{
    <div class="main_inner_cntnr">
        <div class="main_inner_cntnr_top"></div>
        <div class="main_inner_cntnr_middle">
            <div class="head"></div>
};

my $row_count = 10;
my $offset = $q->param('offset') || 0;
$offset *= $row_count;
$limit ||= "LIMIT $offset, $row_count";

my $sth = $dbh->prepare(qq{
    SELECT
        SQL_CALC_FOUND_ROWS
        a.recipe_id,
        a.name,
        a.image,
        a.description,
        DATE_FORMAT(a.added_date, '%M %D, %Y'),
        b.name
    FROM
        recipes AS a,
        users AS b
    WHERE
        a.approved = 1
    AND
        a.user_id = b.user_id
    $cond
    ORDER BY
        a.added_date DESC,
        a.name
    $limit
});
$sth->execute;

my ($result) = $dbh->selectrow_array(qq{SELECT FOUND_ROWS()});
if ($result) {
    print qq{
        <div class="recipes_banner"></div>
        <div class="search_result_cntnr">
    };

    while (my ($recipe_id, $recipe_name, $recipe_image, $description, $added_date, $user_name) = $sth->fetchrow_array) {
        $description = substr($description, 0, 450) . '...' if (length($description) > 450);
        unless ($recipe_image && -e "$GLOB{settings}{files_path}/recipe_images/$recipe_image") {
            $recipe_image = 'no_image.jpg';
        };

        print qq{
            <div style="position:relative; float:left; width:850px; border-bottom:solid 1px #afafaf;">
                <div class="search_result_cntnr_inner">
                    <div style="position:relative; float:left; width:100%; text-align:left;"><a href="$GLOB{settings}{files_url}/item.cgi?recipe_id=$recipe_id">$recipe_name</a></div>
                    <div style="position:relative; float:left; width:90%; left:11px; text-align:left; color:#4f4f4f; font-size:10px;">Added on $added_date by $user_name</div>
                </div>
                <div style="position:relative; float:left; width:100%; text-align:left; min-height:180px;">
                    <div style="position:relative; float:left; width:170px; margin-left:11px; text-align:left;">
                        <img src="$GLOB{settings}{files_url}/recipe_images/$recipe_image" width="150" />
                    </div>
                    <div style="position:relative; float:left; width:600px;margin-top:10px; text-align:left;">
                        $description
                        <div style="position:relative; float:left; width:100%;">
                            <span style="position:relative; float:right; padding:5px; top:15px; text-align:center; background-color:#ff0000; color:#fff;">
                                <a href="$GLOB{settings}{files_url}/item.cgi?recipe_id=$recipe_id" style="text-decoration:none; color:#fff;">View Recipe</a>
                            </span>
                        </div>
                    </div>
                </div>
            </div>
        };
    }

    pagination($result, "$default_url&", $row_count);

    print qq{
        </div>
    };
}
else {
    print qq{
        <div class="head" style="text-align:center;">No recipes found.</div>
    };
}

print qq{
        </div>
        <div class="main_inner_cntnr_btm"></div>
    </div>
};

printFooter();