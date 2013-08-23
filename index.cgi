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

my $sth;

$sth = $dbh->prepare(qq{
    SELECT
        recipe_id,
        name,
        image,
        description
    FROM
        recipes
    WHERE
        top_ten_recipe = 1
    ORDER BY RAND()
});
$sth->execute;

my ($top_ten_recipe_id, $top_ten_recipe_name, $top_ten_recipe_image, $top_ten_recipe_desc);
while (my ($recipe_id, $name, $image, $description) = $sth->fetchrow_array) {
    ($top_ten_recipe_id, $top_ten_recipe_name, $top_ten_recipe_image, $top_ten_recipe_desc) = ($recipe_id, $name, $image, $description);
    last if ($name && -e "$GLOB{settings}{files_path}/recipe_images/$image");
}
$top_ten_recipe_name = substr($top_ten_recipe_name, 0, 25) . '...' if (length($top_ten_recipe_name) > 25);
$top_ten_recipe_image ||= 'no_image.jpg';
$top_ten_recipe_desc = substr($top_ten_recipe_desc, 0, 50) . '...' if (length($top_ten_recipe_desc) > 50);

$sth = $dbh->prepare(qq{
    SELECT
        recipe_id,
        name,
        image,
        description
    FROM
        recipes
    WHERE
        todays_recipe = 1
    ORDER BY RAND()
});
$sth->execute;

my ($todays_recipe_id, $todays_recipe_name, $todays_recipe_image, $todays_recipe_desc);
while (my ($recipe_id, $name, $image, $description) = $sth->fetchrow_array) {
    ($todays_recipe_id, $todays_recipe_name, $todays_recipe_image, $todays_recipe_desc) = ($recipe_id, $name, $image, $description);
    last if ($name && -e "$GLOB{settings}{files_path}/recipe_images/$image");
}
$todays_recipe_name = substr($todays_recipe_name, 0, 25) . '...' if (length($todays_recipe_name) > 25);
$todays_recipe_image ||= 'no_image.jpg';
$todays_recipe_desc = substr($todays_recipe_desc, 0, 50) . '...' if (length($todays_recipe_desc) > 50);

$sth = $dbh->prepare(qq{
    SELECT
        recipe_id,
        name,
        image,
        description
    FROM
        recipes
    WHERE
        easy_recipe = 1
    ORDER BY RAND()
});
$sth->execute;
my ($easy_recipe_id, $easy_recipe_name, $easy_recipe_image, $easy_recipe_desc);
while (my ($recipe_id, $name, $image, $description) = $sth->fetchrow_array) {
    ($easy_recipe_id, $easy_recipe_name, $easy_recipe_image, $easy_recipe_desc) = ($recipe_id, $name, $image, $description);
    last if ($name && -e "$GLOB{settings}{files_path}/recipe_images/$image");
}
$easy_recipe_name = substr($easy_recipe_name, 0, 25) . '...' if (length($easy_recipe_name) > 25);
$easy_recipe_image ||= 'no_image.jpg';
$easy_recipe_desc = substr($easy_recipe_desc, 0, 50) . '...' if (length($easy_recipe_desc) > 50);

print qq{
    <div class="banner_cntnr">
        <div class="left">
            <div class="content">
                Vivid Recipes is your ultimate Indian Food and Recipe Cooking Website offering Cooking Videos, Tips, Recipe Reviews and mouth watering Free Indian food videos with detailed steps of Cooking Instructions in Authentic Indian style.
                We Inspires you to Cook with Perfect ingredients to rekindle your senses, learn the art of impressing your loved ones and inspires you to taste various International Cuisines.
                We combine the ancient with the modern and take you down the path to losing yourself in the exotic flavours of INDIA.
            </div>
        </div>
        <div class="right">
            <div class="cu3er_resize">
                <div id="cu3er-container"><a href="http://www.adobe.com/go/getflashplayer"><img src="http://www.adobe.com/images/shared/download_buttons/get_flash_player.gif" alt="Get Adobe Flash player" /></a></div>
            </div>
        </div>
    </div>

    <div class="special_dish_cntnr">
        <div class="top10">
};

print qq{
            <div class="inner">
                <div class="img"><a href="$GLOB{settings}{files_url}/item.cgi?recipe_id=$top_ten_recipe_id"><img src="$GLOB{settings}{files_url}/recipe_images/$top_ten_recipe_image" width="65" height="50" style="border:none;" alt="" /></a></div>
                <div class="contentcntnr">
                    <div class="contenthead"><a href="$GLOB{settings}{files_url}/item.cgi?recipe_id=$top_ten_recipe_id">$top_ten_recipe_name</a></div>
                    <div class="contentdata">$top_ten_recipe_desc</div>
                    <div class="more"><a href="$GLOB{settings}{files_url}/recipes.cgi?top=1">More...</a></div>
                </div>
            </div>
} if $top_ten_recipe_id;

print qq{
        </div>
        <div class="dishoftheday">
};

print qq{
            <div class="inner">
                <div class="img"><a href="$GLOB{settings}{files_url}/item.cgi?recipe_id=$todays_recipe_id"><img src="$GLOB{settings}{files_url}/recipe_images/$todays_recipe_image" style="border:none;" width="65" height="50" alt="" /></a></div>
                <div class="contentcntnr">
                    <div class="contenthead"><a href="$GLOB{settings}{files_url}/item.cgi?recipe_id=$todays_recipe_id">$todays_recipe_name</a></div>
                    <div class="contentdata">$todays_recipe_desc</div>
                </div>
            </div>
} if $todays_recipe_id;

print qq{
        </div>
        <div class="easydish">
};

print qq{
            <div class="inner">
                <div class="img"><a href="$GLOB{settings}{files_url}/item.cgi?recipe_id=$easy_recipe_id"><img src="$GLOB{settings}{files_url}/recipe_images/$easy_recipe_image" style="border:none;" width="65" height="50" alt="" /></a></div>
                <div class="contentcntnr">
                    <div class="contenthead"><a href="$GLOB{settings}{files_url}/item.cgi?recipe_id=$easy_recipe_id">$easy_recipe_name</a></div>
                    <div class="contentdata">$easy_recipe_desc</div>
                    <div class="more"><a href="$GLOB{settings}{files_url}/recipes.cgi?easy=1">More...</a></div>
                </div>
            </div>
} if $easy_recipe_id;

print qq{
        </div>
    </div>

    <div class="btm">
        <div class="left"></div>
        <div class="middle">
            <div class="name">
                <div class="head" style="color:#960222;">Search By Style</div>
};

for my $style (sort {$a <=> $b} keys %{$GLOB{recipie}{style}}) {
    print qq{
                <div class="inner">
                    <a href="$GLOB{settings}{files_url}/recipes.cgi?style=$style">$GLOB{recipie}{style}{$style}</a>
                </div>
    };
}

for my $category (sort {$a <=> $b} keys %{$GLOB{recipie}{category}}) {
    print qq{
                <div class="inner">
                    <a  href="$GLOB{settings}{files_url}/recipes.cgi?category=$category">$GLOB{recipie}{category}{$category}</a>
                </div>
    };
}

print qq{
            </div>
};

my ($testimonial, $name) = $dbh->selectrow_array(qq{
    SELECT
        a.testimonial,
        b.name
    FROM
        testimonials AS a,
        users AS b
    WHERE
        a.user_id = b.user_id
    ORDER BY RAND()
    LIMIT 1
});
$testimonial =~ s/\r\n|\r|\n/<br>/g;

print qq{
            <div class="testimonials">
                <div class="testi">$testimonial</div>
                <div class="testiname">$name</div>
            </div>
        </div>
        <div class="right"></div>
    </div>
};

printFooter();