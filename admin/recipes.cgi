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
            <div class="head">Recipes</div>
            <div class="topten_cntnr">
};

my $action = $q->param('action');
my $recipe_id = $q->param('id');

if ($action && !$recipe_id) {
    print qq{
        No recipe selected.
    };
}
elsif ($action eq 'edit') {
    editRecipe();
}
elsif ($action eq 'update') {
    updateRecipe();
}
elsif ($action eq 'delete') {
    deleteRecipe();
}
elsif ($action eq 'approve') {
    approveRecipe();
}
else {
    listRecipes();
}

print qq{
            </div>
        </div>
        <div class="main_inner_cntnr_btm"></div>
    </div>
};

printFooter();

sub listRecipes {
    my $default_url = "$GLOB{settings}{files_url}/admin/recipes.cgi?";
    my $row_count = 25;
    my $offset = $q->param('offset') || 0;
    $offset *= $row_count;

    my $search = trim($q->param('search'));
    my $cond;
    if ($search) {
        $search =~ s/'/\\'/g;
        $search =~ s/%/\\%/g;
        $cond = "AND (a.name LIKE '%$search%' OR a.description LIKE '%$search%' OR a.ingredients LIKE '%$search%')";
        $default_url .= 'search=' . uri_escape($search) . '&';
    }

    print qq{
        <div style="position:relative; float:left; width:100%; margin:0 0 10px 100px; text-align:left;">
            <form action="" method="post">
                <input type="text" name="search" value="$search" />
                <input type="submit" value="SEARCH" />
            </form>
        </div>
    };

    my $sth = $dbh->prepare(qq{
        SELECT
            SQL_CALC_FOUND_ROWS
            a.recipe_id,
            a.name,
            a.approved,
            DATE_FORMAT(a.added_date, '%d-%m-%Y') AS added_date,
            b.name
        FROM
            recipes AS a,
            users AS b
        WHERE
            a.user_id = b.user_id
        $cond
        ORDER BY
            a.added_date DESC,
            a.name
        LIMIT $offset, $row_count
    });
    $sth->execute;

    my ($result) = $dbh->selectrow_array(qq{SELECT FOUND_ROWS()});
    if ($result) {
        print qq{
            <div style="position:relative; float:left; width:100%; margin-left:100px; height:20px; padding-top:5px; border:solid 1px #cdcdcd; background-color:#cdcdcd;">
                <div style="position:relative; float:left; width:5%;"><b>#</b></div>
                <div style="position:relative; float:left; width:20%;"><b>User Name</b></div>
                <div style="position:relative; float:left; width:20%;"><b>Recipe Name</b></div>
                <div style="position:relative; float:left; width:15%;"><b>Added Date</b></div>
            </div>
        };

        my $count = $offset;
        while (my ($recipe_id, $recipe_name, $approved, $added_date, $name) = $sth->fetchrow_array) {
            $count++;
            my $class_name = ($count % 2 == 0) ? 'even' : 'odd';
            my $approve_button = $approved ? 'Reject' : 'Approve';

            print qq{
                <div class="$class_name" style="position:relative; float:left; width:100%; margin-left:100px; padding:5px 0 5px 0; border:solid 1px #cdcdcd;">
                    <div style="position:relative; float:left; width:5%;">$count</div>
                    <div style="position:relative; float:left; width:20%;">$name</div>
                    <div style="position:relative; float:left; width:20%;">$recipe_name</div>
                    <div style="position:relative; float:left; width:15%;">$added_date</div>
                    <div style="position:relative; float:left; width:8%;">
                        <a href="$GLOB{settings}{files_url}/item.cgi?recipe_id=$recipe_id"><input type="button" value="View" /></a>
                    </div>
                    <div style="position:relative; float:left; width:8%;">
                        <a href="?action=edit&id=$recipe_id"><input type="button" value="Edit" /></a>
                    </div>
                    <div style="position:relative; float:left; width:10%;">
                        <a href="?action=delete&id=$recipe_id"><input type="button" value="Delete" onclick="if (confirm('Are you sure you want to delete this recipe?') == false) return false;" /></a>
                    </div>
                    <div style="position:relative; float:left; width:10%;">
                        <a href="?action=approve&id=$recipe_id&approved=$approved"><input type="button" value="$approve_button" /></a>
                    </div>
                </div>
            };
        }

        pagination($result, $default_url, $row_count);
    }
    else {
        print qq{
            No recipes
            <a href="$GLOB{settings}{files_url}/admin/index.cgi">Back</a>
        };
    }
}

sub editRecipe {
    my ($recipe_id, $name, $style, $category, $image, $description, $ingredients, $related_recipes) = $dbh->selectrow_array(qq{
        SELECT
            recipe_id,
            name,
            style,
            category,
            image,
            description,
            ingredients,
            related_recipes
        FROM
            recipes
        WHERE
            recipe_id = ?
    }, undef, $recipe_id);

    if (!$recipe_id) {
        print qq{
            This recipe does not exist.
        };
    }
    else {
        my @style = split /,/, $style;
        my @category = split /,/, $category;
        my @related_recipes = split /,/, $related_recipes;

        my %selected;
        for (@style) {
            $selected{style}{$_} = qq{ selected="selected"};
        }
        for (@category) {
            $selected{category}{$_} = qq{ selected="selected"};
        }
        for (@related_recipes) {
            $selected{related_recipes}{$_} = qq{ selected="selected"};
        }

        my $image_link;
        if ($image && -e "$GLOB{settings}{files_path}/recipe_images/$image") {
            $image_link = qq{<a href="$GLOB{settings}{files_url}/recipe_images/$image" target="_blank">View</a>};
        }

        print qq{
            <form action="" method="post" enctype="multipart/form-data">
                <div class="signupdatacntnr">
                    <div class="inner">
                        <div class="tp">
                            <div>Name:</div>
                            <div><input type="text" name="name" id="name" value="$name" /></div>
                        </div>
                        <div class="tp">
                            <div>Style:<br>(Hold Ctrl key to select multiple options)</div>
                            <div>
                                <select name="style" multiple="multiple" size="5">
                                    <option value="">Select</option>
        };

        for my $style (sort {$a <=> $b} keys %{$GLOB{recipie}{style}}) {
            print qq{
                                    <option value="$style"$selected{style}{$style}>$GLOB{recipie}{style}{$style}</option>
            };
        }

        print qq{
                                </select>
                            </div>
                        </div>
                        <div class="tp">
                            <div>Category:<br>(Hold Ctrl key to select multiple options)</div>
                            <div>
                                <select name="category" multiple="multiple" size="5">
                                    <option value="">Select</option>
        };

        for my $category (sort {$a <=> $b} keys %{$GLOB{recipie}{category}}) {
            print qq{
                                    <option value="$category"$selected{category}{$category}>$GLOB{recipie}{category}{$category}</option>
            };
        }

        print qq{
                                </select>
                            </div>
                        </div>
                        <div class="tp">
                            <div>Related Recipes:<br>(Hold Ctrl key to select multiple options)</div>
                            <div>
                                <select name="related_recipes" multiple="multiple" size="5" style="width:auto;">
                                    <option value="">Select</option>
        };

        my $sth = $dbh->prepare(qq{
            SELECT
                recipe_id,
                name
            FROM
                recipes
            WHERE
                recipe_id != ?
            AND
                approved = 1
            ORDER BY
                name
        });
        $sth->execute($recipe_id);
        while (my ($recipe_id, $recipe_name) = $sth->fetchrow_array) {
            print qq{
                                    <option value="$recipe_id"$selected{related_recipes}{$recipe_id}>$recipe_name</option>
            };
        }

        print qq{
                                </select>
                            </div>
                        </div>
                        <div class="tp">
                            <div>Image:</div>
                            <div><input type="file" name="image" id="image" />$image_link</div>
                        </div>
                        <div class="tp">
                            <div>Ingredients:</div>
                            <div><textarea name="ingredients" style="width:400px; height:250px;">$ingredients</textarea></div>
                        </div>
                        <div class="tp">
                            <div>Description:</div>
                            <div><textarea name="description" style="width:400px; height:250px;">$description</textarea></div>
                        </div>
                        <div class="tp">
                            <div>
                                <input type="hidden" name="id" value="$recipe_id" />
                                <input type="hidden" name="action" value="update" />
                                <input type="submit" value="Update" onclick="return validateForm();" style="background-color:#420100; color:#fff; cursor:pointer;" />
                            </div>
                        </div>
                    </div>
                </div>
            </form>
        };
    }

    print qq{
        <a href="$GLOB{settings}{files_url}/admin/recipes.cgi">Back</a>
    };
}

sub updateRecipe {
    my ($recipe_id, $old_image) = $dbh->selectrow_array(qq{
        SELECT
            recipe_id,
            image
        FROM
            recipes
        WHERE
            recipe_id = ?
    }, undef, $recipe_id);

    my $name = trim($q->param('name'));
    my @style = $q->param('style');
    my @category = $q->param('category');
    my @related_recipes = $q->param('related_recipes');
    my $image = $q->upload('image');
    my $description = trim($q->param('description')) || undef;
    my $ingredients = trim($q->param('ingredients')) || undef;

    if (!$recipe_id) {
        print qq{
            This recipe does not exist.
        };
    }
    elsif (!$name) {
        print qq{
            Please enter name.
        };
    }
    else {
        my $new_image = $old_image;
        if ($image) {
            my $user_id = $GLOB{user}{user_id};
            my @splits = split /\\/, $image;
            my ($file_name, $extension) = split("\\.", $splits[-1]);

            $new_image = "${file_name}_${user_id}_" . time . ".$extension";

            open (UPLOADFILE, ">$GLOB{settings}{files_path}/recipe_images/$new_image") or die "$!";
            while (<$image>) {
                print UPLOADFILE;
            }
            close UPLOADFILE;
        }

        @style = grep {/^\d+$/} @style;
        my $style = join(',', @style) || undef;

        @category = grep {/^\d+$/} @category;
        my $category = join(',', @category) || undef;

        @related_recipes = sort {$a <=> $b} grep {/^\d+$/} @related_recipes;
        my $related_recipes = join(',', @related_recipes) || undef;

        $dbh->do(qq{
            UPDATE
                recipes
            SET
                name = ?,
                style = ?,
                category = ?,
                image = ?,
                description = ?,
                ingredients = ?,
                related_recipes = ?
            WHERE
                recipe_id = ?
        }, undef, $name, $style, $category, $new_image, $description, $ingredients, $related_recipes, $recipe_id);

        if ($image && $old_image && -e "$GLOB{settings}{files_path}/recipe_images/$old_image") {
            unlink "$GLOB{settings}{files_path}/recipe_images/$old_image";
        }

        print qq{
            Recipe updated successfully.
        };
    }

    print qq{
        <a href="$GLOB{settings}{files_url}/admin/recipes.cgi">Back</a>
    };
}

sub deleteRecipe {
    my ($recipe_id, $image) = $dbh->selectrow_array(qq{
        SELECT
            recipe_id,
            image
        FROM
            recipes
        WHERE
            recipe_id = ?
    }, undef, $recipe_id);

    if (!$recipe_id) {
        print qq{
            This recipe does not exist.
        };
    }
    else {
        $dbh->do(qq{
            DELETE FROM
                recipes
            WHERE
                recipe_id = ?
        }, undef, $recipe_id);

        if ($image && -e "$GLOB{settings}{files_path}/recipe_images/$image") {
            unlink "$GLOB{settings}{files_path}/recipe_images/$image";
        }

        print qq{
            Recipe deleted successfully.
        };
    }

    print qq{
        <a href="$GLOB{settings}{files_url}/admin/recipes.cgi">Back</a>
    };
}

sub approveRecipe {
    my ($recipe_id) = $dbh->selectrow_array(qq{
        SELECT
            recipe_id
        FROM
            recipes
        WHERE
            recipe_id = ?
    }, undef, $recipe_id);

    if (!$recipe_id) {
        print qq{
            This recipe does not exist.
        };
    }
    else {
        my $approved = $q->param('approved');
        my %approved = (
            0 => {
                update => 1,
                message => 'approved',
            },
            1 => {
                update => 0,
                message => 'rejected',
            },
        );

        $dbh->do(qq{
            UPDATE
                recipes
            SET
                approved = ?
            WHERE
                recipe_id = ?
        }, undef, $approved{$approved}{update}, $recipe_id);

        print qq{
            Recipe $approved{$approved}{message} successfully.
        };
    }

    print qq{
        <a href="$GLOB{settings}{files_url}/admin/recipes.cgi">Back</a>
    };
}

sub printJSFunctions {
    print qq{
        <script type="text/javascript">
            function validateForm() {
                var name = document.getElementById('name').value;
                var image = document.getElementById('image').value;

                if (name == '' || name == null) {
                    alert('Please enter name');
                    document.getElementById('name').focus();
                    return false;
                }

                if (image != '' && image != null) {
                    var extn = image.slice(image.indexOf('.')).toLowerCase();
                    if (extn != '.jpg' && extn != '.jpe' && extn != '.jpeg' && extn != '.gif' && extn != '.png') {
                        alert('Please select valid image file');
                        return false;
                    }
                }

                return true;
            }
        </script>
    };
}