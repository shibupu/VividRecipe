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

&checkSession(refererCheck => 0, postCheck => 0);

print $q->header();
printHeader();
printJSFunctions();

my $action = $q->param('action');
if ($action) {
    my $user_id = $GLOB{user}{user_id};
    my $name = trim($q->param('name'));
    my @style = $q->param('style');
    my @category = $q->param('category');
    my $image = $q->upload('image');
    my $description = trim($q->param('description')) || undef;
    my $ingredients = trim($q->param('ingredients')) || undef;

    if (!$name) {
        print qq{
            <div class="head">Please enter name.</div>
        };
    }
    else {
        my $new_image;
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

        my $approved = ($GLOB{user}{email} eq 'admin') ? 1 : 0;

        $dbh->do(qq{
            INSERT INTO
                recipes
                (user_id, name, style, category, image, description, ingredients, approved)
            VALUES
                (?, ?, ?, ?, ?, ?, ?, ?)
        }, undef, $user_id, $name, $style, $category, $new_image, $description, $ingredients, $approved);

        print qq{
            <div class="head">Recipie added successfully.</div>
        };
    }

    print qq{
        <a href="$GLOB{settings}{files_url}/index.cgi">Home</a>
    };
}
else {
    print qq{
        <div class="main_inner_cntnr">
            <div class="main_inner_cntnr_top"></div>
            <div class="main_inner_cntnr_middle">
                <div class="head">Add Recipes</div>
                <form action="" method="post" enctype="multipart/form-data">
                    <div class="signupdatacntnr">
                        <div class="inner">
                            <div class="tp">
                                <div >Name:</div>
                                <div ><input style="width:230px;" type="text" name="name" id="name" /></div>
                            </div>
                            <div class="tp">
                                <div>Style:<br>(Hold Ctrl key to select multiple options)</div>
                                <div>
                                    <select name="style" multiple="multiple" size="5">
                                        <option value="">Select</option>
    };

    for my $style (sort {$a <=> $b} keys %{$GLOB{recipie}{style}}) {
        print qq{
                                        <option value="$style">$GLOB{recipie}{style}{$style}</option>
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
                                        <option value="$category">$GLOB{recipie}{category}{$category}</option>
        };
    }

    print qq{
                                    </select>
                                </div>
                            </div>
                            <div class="tp">
                                <div>Image:</div>
                                <div><input type="file" name="image" id="image" /></div>
                            </div>
                            <div class="tp">
                                <div>Ingredients:</div>
                                <div><textarea name="ingredients" style="width:400px; height:250px;"></textarea></div>
                            </div>
                            <div class="tp">
                                <div>Description:</div>
                                <div><textarea name="description" style="width:400px; height:250px;"></textarea></div>
                            </div>
                            <div class="tp">
                                <div>
                                    <input type="hidden" name="action" value="add" />
                                    <input type="submit" value="Add" onclick="return validateForm();" style="background-color:#420100; color:#fff; cursor:pointer;" />
                                </div>
                            </div>
                        </div>
                    </div>
                </form>
            </div>
            <div class="main_inner_cntnr_btm"></div>
        </div>
    };
}

printFooter();

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