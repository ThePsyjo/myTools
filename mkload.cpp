
/************************************************************************
 * mkload.cpp								*
 * Copyright (C) 2008,2009  Psyjo					*
 *									*
 * This program is free software; you can redistribute it and/or modify	*
 * it under the terms of the GNU General Public License as published by	*
 * the Free Software Foundation; either version 3 of the License,	*
 * or (at your option) any later version.				*
 *									*
 * This program is distributed in the hope that it will be useful, but	*
 * WITHOUT ANY WARRANTY; without even the implied warranty of		*
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.			*
 * See the GNU General Public License for more details.			*
 *									*
 * You should have received a copy of the GNU General Public License	*
 * along with this program; if not, see <http://www.gnu.org/licenses/>. *
 ************************************************************************/
#include <cstdio>
#include <stdlib.h>
#include <unistd.h>
#include <signal.h>
#include <sys/time.h>
#include <pthread.h>

int running;

void killThrd(int i){running = 0;}

void *load(void *threadid)
{
	while(running)7/3;
	pthread_exit(NULL);
}

int main(int n, char** v)
{
	int thrdCnt, sec, rc, t;
	struct itimerval tv;

	running = 1;

	switch(n)
	{
	case 3:
		thrdCnt = atoi(v[1]);
		sec = atoi(v[2]);
		break;
	case 2:
		thrdCnt = 1;
		sec = atoi(v[1]);
		break;
	default: 
		printf("mkload (C) 2008 by Psyjo\nusage: %s [<number of threads/cores>] <time in seconds>\n0 secs -> infinite runtime\n", v[0]);
		exit(1);
		break;
	}
			
	tv.it_interval.tv_sec=0;
	tv.it_interval.tv_usec=0;
	tv.it_value.tv_sec=sec;
	tv.it_value.tv_usec=0;

	signal(SIGALRM, &killThrd);

	pthread_t threads[thrdCnt];
	for(t=0; t<thrdCnt; t++){
		rc = pthread_create(&threads[t], NULL, load, (void *)NULL);
		if (rc){
			printf("ERROR; return code from pthread_create() is %d\n", rc);
			exit(-1);
		}
	}

	if (setitimer(ITIMER_REAL, &tv, NULL) <0) puts("set timer fail"); // throw message
	else pthread_exit(NULL); // wait 4 exit
}
