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
            <div class="head">Dish Of The Day</div>
            <div class="topten_cntnr">
};

my $action = $q->param('action');
if ($action) {
    my @recipe_id = $q->param('recipe_id');

    if (!@recipe_id) {
        print qq{
            Please select the recipe.
            <a href="$GLOB{settings}{files_url}/admin/todays_recipe.cgi">Back</a>
        };
    }
    elsif (@recipe_id > 1) {
        print qq{
            Please select only 1 recipe.
            <a href="$GLOB{settings}{files_url}/admin/todays_recipe.cgi">Back</a>
        };
    }
    else {
        $dbh->do(qq{
            UPDATE
                recipes
            SET
                todays_recipe = 0
        });

        my $recipe_id = $recipe_id[0];
        $dbh->do(qq{
            UPDATE
                recipes
            SET
                todays_recipe = 1
            WHERE
                recipe_id = ?
        }, undef, $recipe_id) if ($recipe_id);

        print qq{
            Recipes added successfully.
            <a href="$GLOB{settings}{files_url}/admin/index.cgi">Back</a>
        };
    }
}
else {
    my $sth = $dbh->prepare(qq{
        SELECT
            SQL_CALC_FOUND_ROWS
            recipe_id,
            name,
            todays_recipe
        FROM
            recipes
        ORDER BY
            name
    });
    $sth->execute;
    my ($result) = $dbh->selectrow_array(qq{SELECT FOUND_ROWS()});
    if ($result) {
        my %checked;
        $checked{todays_recipe}{1} = qq{ checked="checked"};

        print qq{
             <div style="position:relative; float:left; width:800px; left:30px;">
                <form action="" method="post">
        };

        while (my ($recipe_id, $name, $todays_recipe) = $sth->fetchrow_array) {
            print qq{
                    <div style="position:relative; float:left; width:90%; height:32px; text-align:left;">
                        <span style="width:25px;"><input type="radio" name="recipe_id" value="$recipe_id"$checked{todays_recipe}{$todays_recipe} /></span>
                        <span><a href="$GLOB{settings}{files_url}/item.cgi?recipe_id=$recipe_id" target="_blank">$name</a></span>
                    </div>
            };
        }
        
        print qq{
                    <div style="position:relative; float:left; width:100%;">
                        <input type="hidden" name="action" value="add" />
                        <input type="submit" value="Add" onclick="return validateForm();" />
                        <a href="$GLOB{settings}{files_url}/admin/index.cgi" style="width:100px; height:25px; background-color:#420100; color:#fff; cursor:pointer;">Back</a>
                    </div>
                </form>
            </div>
        };
    }
    else {
        print qq{
            No recipes
            <a href="$GLOB{settings}{files_url}/admin/index.cgi">Back</a>
        };
    }
}

print qq{
            </div>
        </div>
        <div class="main_inner_cntnr_btm"></div>
    </div>
};

printFooter();

sub printJSFunctions {
    print qq{
        <script type="text/javascript">
            function validateForm() {
                var recipe_id = document.getElementsByName('recipe_id');
                var checked_recipes = 0;
                for (var i = 0; i < recipe_id.length; i++) {
                    if (recipe_id[i].checked) checked_recipes++;
                }

                if (checked_recipes == 0) {
                    alert('Please select the recipe');
                    return false;
                }

                return true;
            }
        </script>
    };
}