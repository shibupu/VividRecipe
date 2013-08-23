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

print qq{
    <div class="main_inner_cntnr">
        <div class="main_inner_cntnr_top"></div>
        <div class="main_inner_cntnr_middle">
            <div class="head"></div>
            <div class="item_cntnr">
                <div class="inner">
};

my $recipe_id = $q->param('recipe_id');
if ($recipe_id) {
    my ($name, $image, $description, $ingredients, $related_recipes) = $dbh->selectrow_array(qq{
        SELECT
            name,
            image,
            description,
            ingredients,
            related_recipes
        FROM
            recipes
        WHERE
            recipe_id = ?
    }, undef, $recipe_id);

    $description =~ s/\r\n|\r|\n/<br>/g;
    $ingredients =~ s/\r\n|\r|\n/<br>/g;

    print qq{
                    <div class="name">$name</div>
                    <div class="inci_img">
                        <div class="inner">
                            <div class="reciepehead">Ingredients</div>
                            <div class="incr">$ingredients</div>
                        </div>
    };

    if ($image && -e "$GLOB{settings}{files_path}/recipe_images/$image") {
        print qq{
                        <div class="inner">
                            <div class="dish_cntnr">
                                <img src="$GLOB{settings}{files_url}/recipe_images/$image" width="300" />
                            </div>
                        </div>
        };
    }

    print qq{
                    </div>
                    <div class="reciepehead">Preparation of $name</div>
                    <div class="incr">$description</div>
    };

    if ($related_recipes =~ /\d+/) {
        print qq{
                    <div class="reciepehead">Related Recipes</div>
        };

        my $sth = $dbh->prepare(qq{
            SELECT
                recipe_id,
                name,
                image
            FROM
                recipes
            WHERE
                recipe_id IN ($related_recipes)
            ORDER BY
                name
        });
        $sth->execute;
        while (my ($recipe_id, $recipe_name, $recipe_image) = $sth->fetchrow_array) {
            unless ($recipe_image && -e "$GLOB{settings}{files_path}/recipe_images/$recipe_image") {
                $recipe_image = 'no_image.jpg';
            };

            print qq{
                <div class="search_result_cntnr_inner">
                    <div style="position:relative; float:left; width:100%; text-align:left;"><a href="$GLOB{settings}{files_url}/item.cgi?recipe_id=$recipe_id">$recipe_name</a></div>
                    <div style="position:relative; float:left; width:170px; margin-left:11px; text-align:left;">
                        <img src="$GLOB{settings}{files_url}/recipe_images/$recipe_image" width="65" height="50" />
                    </div>
                </div>
            };
        }
    }
}
else {
    print qq{
        <div class="head" style="text-align:center;">No recipe selected</div>
    };
}

print qq{
                </div>
            </div>
            <div class="right_sty">
                <div class="inner">
};

for my $style (sort {$a <=> $b} keys %{$GLOB{recipie}{style}}) {
    print qq{
                    <div class="sty">
                        <a href="$GLOB{settings}{files_url}/recipes.cgi?style=$style">$GLOB{recipie}{style}{$style}</a>
                    </div>
    };
}

for my $category (sort {$a <=> $b} keys %{$GLOB{recipie}{category}}) {
    print qq{
                    <div class="sty">
                        <a href="$GLOB{settings}{files_url}/recipes.cgi?category=$category">$GLOB{recipie}{category}{$category}</a>
                    </div>
    };
}

print qq{
                </div>
            </div>
        </div>
        <div class="main_inner_cntnr_btm"></div>
    </div>
};

printFooter();