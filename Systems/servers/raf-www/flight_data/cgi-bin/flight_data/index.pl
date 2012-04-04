#!/usr/bin/perl -T
#
# COPYRIGHT: University Corporation for Atmospheric Research, 2009-12
#

use strict;
use CGI qw(:all);

our $q; our %plat_vars;
require "./getCookie.pl";

&makeMenu();


sub makeMenu {
my $p=$plat_vars{'platform'};

if ($p ne 'acserver'){
	my $c = new CGI::Cookie(-name=>'platform', -value=>$p, -expires=>"+24h");
	print $q->header(-cookie=>$c);
}

&stdHTML;

#menu.html file contains the setup for the top-bar menu.
# This may need to be adjusted per project.
open FILE, "<", $plat_vars{'docs_path'}."display/menu.html" or die "could not read menu.html";
my @menu=<FILE>;
close FILE or die "could not close file";
print @menu;

&stdEndHTML;
}

sub stdHTML {

print <<endHTML2;

<html>
	<head>
		<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1" />
		<title>Display</title>
		<link rel="icon" type="image/png" href="$plat_vars{base_path}display/favicon.png" />

		<style type="text/css">
			body {
				margin: 0px; padding: 0px;
				font: bold 1.1em "Arial",sans-serif;
			}
			div.clear {clear: both;}
			#nav {margin-top: 1px;}
			#nav div {
				float:	left;
				width: 105px;
				height: 40px;
				background: url('$plat_vars{base_path}display/button-t.png') no-repeat center;
				color: #FFF;
				text-align: center;
				line-height: 240%;
				cursor: pointer;
				margin-right: .07em;
			}
			span.pform {
				float: left;
				/*width: 60px;*/
				height: 50px;
				background: none;
				font-size: 25px;
				padding: 5px 0 0 5px;
			}
			span.pform a {
				color: #000;
				text-decoration: none;
			}
			#nav div.nosel_hover {
				background: url('$plat_vars{base_path}display/button2-t.png') no-repeat top;
			}
			#nav div.sel {
				background: url('$plat_vars{base_path}display/button2-t.png') no-repeat top;
				margin-top: .15em; margin-left: .15em; /*give 'pushed in' look*/
			} 
			#nav div.superMenu {
				background: transparent;
				top: -5px;
				padding-top: 5px;
				position: relative;
				z-index: 10;
				display: none;
			}
			#nav div.superMenuLabel_hover {
				background: url('$plat_vars{base_path}display/button2-t.png') no-repeat top;
			}
			#nav div.superMenuLabel_hover div.superMenu {
				height: auto;
				display: block;
			} 
			div.box { 
				position: absolute;
				left: 0px;
				top: 0px;
				min-width: 660px; /*prevents odd behavior w/ small browser window */
				width: 100%;
				height: 42px;
				background: url('$plat_vars{base_path}display/bg-grad-s.png') repeat-x;
			}
			#cont {
				margin-top: 42px;
			}
		</style>

		<script type="text/javascript">
			var curpage, buttonlist, numButtons=8;
			function tabSelect(tab) {
				for (var i=0; i<buttonlist.length; i++){ 
					if (buttonlist[i].className.slice(0,5) != "super") {
						buttonlist[i].className = "nosel";
					}
				}
				tab.className = "sel";	
				for (var i=0; i<buttonlist.length; i++){ 
					if (buttonlist[i].className == "sel") { curpage = i; }
				}
				document.getElementById('cObj').src=tab.title;
				setCookie("display_page", curpage, 1);
			}
			function windowResize() {
				var winheight = document.body.clientHeight;
				document.getElementById('cObj').height = winheight - 42;
			}
			function init() {
				buttonlist = document.getElementById('nav').getElementsByTagName('div');
				for (var i in buttonlist) {
					buttonlist[i].onmouseover = function() { 
						var cn = this.className;
						if (cn == "nosel" || cn == "superMenuLabel"){
							this.className += "_hover";
						}
					 }
					buttonlist[i].onmouseout = function() { this.className = this.className.split("_",1); }
				}	
	
				curpage = getCookie("display_page");
				var load_page = curpage == "" ? 0 : curpage;
				tabSelect(buttonlist[load_page]);

				var minsize = numButtons * 107;
				document.getElementById('navbox').style.minWidth = minsize+"px";
				windowResize();
			}
			function setCookie(c_name, value, expire_days) {
				var exdate=new Date();
				exdate.setDate(exdate.getDate()+expire_days);
				document.cookie=c_name+ "=" +escape(value)+
				((expire_days==null) ? "" : ";expires="+exdate.toGMTString());
			}
			function getCookie(c_name)
			{
			    if (document.cookie.length>0)
			    {
				c_start=document.cookie.indexOf(c_name + "=");
				if (c_start!=-1)
				{
				    c_start=c_start + c_name.length+1;
				    c_end=document.cookie.indexOf(";",c_start);
				    if (c_end==-1) c_end=document.cookie.length;
				    return unescape(document.cookie.substring(c_start,c_end));
				}
			    }
			    return "";
			}
			
			window.onload=init;
			window.onresize=windowResize;
		</script>
	</head>

	<body>
		<div class="box" id="navbox"> 
			<div id="nav">
endHTML2
}

sub stdEndHTML {
print <<endHTML3;
			</div>
			<div class="clear"></div>
		</div> 
		<div id="cont">
			<iframe id="cObj" width="100%" height="100%" frameborder="0" scrolling="auto" ></iframe>
		</div>
	</body>

</html>

endHTML3
}
