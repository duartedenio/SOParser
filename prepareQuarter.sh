#!/bin/bash
echo "This script will prepare the stackoverflow data with time slice equals a quarter"



# Data must already be download, and folder rawdata must exist (as well 2013.Posts.xml and 2014.Posts.xml)
cd rawdata

echo "splitting files 2013 in quarters"
M20131st=`awk '/CreationDate=\"2013-01/ {print NR; exit}' 2013.Posts.xml`
M20132nd=`awk '/CreationDate=\"2013-04/ {print NR; exit}' 2013.Posts.xml`
LAST=`expr $M20132nd - 1`
awk 'NR=='$M20131st', NR=='$LAST'-1; NR=='$LAST' {print; exit}' 2013.Posts.xml > 2013-1stQ.Posts.xml
echo "2013-1st quarter done"


M20133rd=`awk '/CreationDate=\"2013-07/ {print NR; exit}' 2013.Posts.xml`
LAST=`expr $M20133rd - 1`
awk 'NR=='$M20132nd', NR=='$LAST'-1; NR=='$LAST' {print; exit}' 2013.Posts.xml > 2013-2ndQ.Posts.xml
echo "2013-2nd Quarter done"

M20134th=`awk '/CreationDate=\"2013-10/ {print NR; exit}' 2013.Posts.xml`
LAST=`expr $M20134th - 1`
awk 'NR=='$M20133rd', NR=='$LAST'-1; NR=='$LAST' {print; exit}' 2013.Posts.xml > 2013-3rdQ.Posts.xml
echo "2013-3rd Quarter done"

awk 'NR>='$M20134th 2013.Posts.xml > 2013-4thQ.Posts.xml
echo "2013-4th Quarter done"

####
echo "splitting files 2014 in quarters"
M20141st=`awk '/CreationDate=\"2014-01/ {print NR; exit}' 2014.Posts.xml`
M20142nd=`awk '/CreationDate=\"2014-04/ {print NR; exit}' 2014.Posts.xml`
LAST=`expr $M20142nd - 1`
awk 'NR=='$M20141st', NR=='$LAST'-1; NR=='$LAST' {print; exit}' 2014.Posts.xml > 2014-1stQ.Posts.xml
echo "2014-1st quarter done"


M20143rd=`awk '/CreationDate=\"2014-07/ {print NR; exit}' 2014.Posts.xml`
LAST=`expr $M20143rd - 1`
awk 'NR=='$M20142nd', NR=='$LAST'-1; NR=='$LAST' {print; exit}' 2014.Posts.xml > 2014-2ndQ.Posts.xml
echo "2014-2nd Quarter done"

M20144th=`awk '/CreationDate=\"2014-10/ {print NR; exit}' 2014.Posts.xml`
LAST=`expr $M20144th - 1`
awk 'NR=='$M20143rd', NR=='$LAST'-1; NR=='$LAST' {print; exit}' 2014.Posts.xml > 2014-3rdQ.Posts.xml
echo "2014-3rd Quarter done"

awk 'NR>='$M20144th 2014.Posts.xml > 2014-4thQ.Posts.xml
echo "2014-4th Quarter done"

cd ..
