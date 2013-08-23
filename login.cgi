#!/usr/bin/perl

#-------------------------------------------------------------------------------
# Modules Required
use CGI;
use vars qw(%GLOB $q $dbh);
use CGI::Carp qw(fatalsToBrowser);
use strict;
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
# Libraries Required
require "cgi-bin/vivid.conf";
require "session.pl";
require "common.pl";
#-------------------------------------------------------------------------------

$q = new CGI;
$CGI::HEADERS_ONCE = 1;

#-------------------------------------------------------------------------------
# Database Connection
($dbh) = &getDatabaseConnection();
#-------------------------------------------------------------------------------

&checkSession(refererCheck => 0, postCheck => 0);

my $email = $GLOB{user}{email};
my $url = ($email eq 'admin') ? './admin/index.cgi' : 'index.cgi';
print $q->redirect($url);