/*
 *  ##############################
 *  #        fixname.cpp         #
 *  #                            #
 *  #         2007-2008 Psyjo©   #
 *  ##############################
 *  # Distributed under the terms of the GNU General Public License v2
 */
#include <cstdio>
#include <string>
#include <stdlib.h>
#include "stringfixer.h"
#define BUFSIZE 1024

int main(int argc, char **arg)
{
	unsigned set, space;
	argc--;
	if (argc > 0)
	{
		set=atoi(arg[1]);
		if(argc>1)
			space=atoi(arg[2]);
		else space=0;
	}
	else
	{
		set=3;
		space=1;
	}

	Stringfixer fix (set, space);

	char buf[BUFSIZE];
	while (fgets(buf, BUFSIZE, stdin))
    		//printf("%s", fix.badStr2HtmlStr(buf).c_str());
    		printf("%s", fix.badStr2Str(buf).c_str()); // to ASCII
}
