/*
 *  ##############################
 *  #        stringfixer.h       #
 *  #                            #
 *  #            2008 (c) Psyjo� #
 *  ##############################
 *  # Distributed under the terms of the GNU General Public License v3
 */
#ifndef STRINGFIXER_H
#define STRINGFIXER_H

#include <stdlib.h>
#include <string>
#include <map>
#ifdef FIXER_STATS
#include <cstdio>
#endif
using namespace std;

class Stringfixer
{
public:
	Stringfixer();
	Stringfixer(int);
	Stringfixer(int, int);
	~Stringfixer();
	
	string badC2Str(char);
	string badC2Html(char);

	string badStr2Str(string);
	string badStr2HtmlStr(string);
private:
	unsigned cnt;
	#ifdef FIXER_STATS
	unsigned i,f;
	#endif
	void setup(int, int);
	map<char, string> *strMap;
	map<char, string> *htmMap;
};

Stringfixer::Stringfixer()				{setup(4, 0);}
Stringfixer::Stringfixer(int level)			{setup(level, 0);}
Stringfixer::Stringfixer(int level, int spacelevel)	{setup(level, spacelevel);}

void Stringfixer::setup(int level, int spacelevel)
{
	#ifdef FIXER_STATS
	i = 0;f = 0;
	#endif

	strMap = new map<char, string>;
	htmMap = new map<char, string>;

	(*htmMap)[' ']="&nbsp;";
	(*htmMap)['�']="&iexcl;";
	(*htmMap)['�']="&cent;";
	(*htmMap)['�']="&pound;";
	(*htmMap)['�']="&curren;";
	(*htmMap)['�']="&yen;";
	(*htmMap)['�']="&brvbar;";
	(*htmMap)['�']="&sect;";
	(*htmMap)['�']="&uml;";
	(*htmMap)['�']="&copy;";
	(*htmMap)['�']="&ordf;";
	(*htmMap)['�']="&laquo;";
	(*htmMap)['�']="&not;";
	(*htmMap)['�']="&reg;";
	(*htmMap)['�']="&macr;";
	(*htmMap)['�']="&deg;";
	(*htmMap)['�']="&plusmn;";
	(*htmMap)['�']="&sup2;";
	(*htmMap)['�']="&sup3;";
	(*htmMap)['�']="&acute;";
	(*htmMap)['�']="&micro;";
	(*htmMap)['�']="&para;";
	(*htmMap)['�']="&middot;";
	(*htmMap)['�']="&cedil;";
	(*htmMap)['�']="&sup1;";
	(*htmMap)['�']="&ordm;";
	(*htmMap)['�']="&raquo;";
	(*htmMap)['�']="&frac14;";
	(*htmMap)['�']="&frac12;";
	(*htmMap)['�']="&frac34;";
	(*htmMap)['�']="&iquest;";
	(*htmMap)['�']="&Agrave;";
	(*htmMap)['�']="&Aacute;";
	(*htmMap)['�']="&Atilde;";
	(*htmMap)['�']="&Acirc;";
	(*htmMap)['�']="&Auml;";
	(*htmMap)['�']="&AElig;";
	(*htmMap)['�']="&Ccedil;";
	(*htmMap)['�']="&Egrave;";
	(*htmMap)['�']="&Eacute;";
	(*htmMap)['�']="&Ecirc;";
	(*htmMap)['�']="&Euml;";
	(*htmMap)['�']="&Igrave;";
	(*htmMap)['�']="&Iacute;";
	(*htmMap)['�']="&Icirc;";
	(*htmMap)['�']="&Iuml;";
	(*htmMap)['�']="&ETH;";
	(*htmMap)['�']="&Ntilde;";
	(*htmMap)['�']="&Ograve;";
	(*htmMap)['�']="&Oacute;";
	(*htmMap)['�']="&Ocirc;";
	(*htmMap)['�']="&Otilde;";
	(*htmMap)['�']="&Ouml;";
	(*htmMap)['�']="&times;";
	(*htmMap)['�']="&Oslash;";
	(*htmMap)['�']="&Ugrave;";
	(*htmMap)['�']="&Uacute;";
	(*htmMap)['�']="&Ucirc;";
	(*htmMap)['�']="&Uuml;";
	(*htmMap)['�']="&Yacute;";
	(*htmMap)['�']="&THORN;";
	(*htmMap)['�']="&szlig;";
	(*htmMap)['�']="&agrave;";
	(*htmMap)['�']="&aacute;";
	(*htmMap)['�']="&acirc;";
	(*htmMap)['�']="&atilde;";
	(*htmMap)['�']="&auml;";
	(*htmMap)['�']="&aring;";
	(*htmMap)['�']="&aelig;";
	(*htmMap)['�']="&ccedil;";
	(*htmMap)['�']="&egrave;";
	(*htmMap)['�']="&eacute;";
	(*htmMap)['�']="&ecirc;";
	(*htmMap)['�']="&euml;";
	(*htmMap)['�']="&igrave;";
	(*htmMap)['�']="&iacute;";
	(*htmMap)['�']="&icirc;";
	(*htmMap)['�']="&iuml;";
	(*htmMap)['�']="&eth;";
	(*htmMap)['�']="&ntilde;";
	(*htmMap)['�']="&ograve;";
	(*htmMap)['�']="&oacute;";
	(*htmMap)['�']="&ocirc;";
	(*htmMap)['�']="&otilde;";
	(*htmMap)['�']="&ouml;";
	(*htmMap)['�']="&divide;";
	(*htmMap)['�']="&oslash;";
	(*htmMap)['�']="&ugrave;";
	(*htmMap)['�']="&uacute;";
	(*htmMap)['�']="&ucirc;";
	(*htmMap)['�']="&uuml;";
	(*htmMap)['�']="&yacute;";
	(*htmMap)['�']="&thorn;";
	(*htmMap)['�']="&yuml;";


	if ( spacelevel > 0 )
		(*strMap)[' ']="_"; // "&nbsp;"
	
	if (level > 0)
	{
		(*strMap)['�']="i"; // "&iexcl;"
		(*strMap)['�']="c"; // "&cent;"
		(*strMap)['�']="[Pfund]"; // "&pound;"
		(*strMap)['�']="[Yen]"; // "&yen;"
		(*strMap)['�']="|"; // "&brvbar;"
		(*strMap)['�']="_"; // "&ordf;"
		(*strMap)['�']="_"; // "&ordm;"
		(*strMap)['�']="<<"; // "&laquo;"
		(*strMap)['�']=">>"; // "&raquo;"
		(*strMap)['�']="_"; // "&not;"
		(*strMap)['�']="-"; // "&macr;"
		(*strMap)['�']="+-"; // "&plusmn;"
		(*strMap)['�']="x"; // "&times;"
		(*strMap)['�']="^2"; // "&sup2;"
		(*strMap)['�']="^3"; // "&sup3;"
		(*strMap)['�']="_"; // "&acute;"
		(*strMap)['�']="[mu]"; // "&micro;"
		(*strMap)['�']="_"; // "&para;"
		(*strMap)['�']="-"; // "&middot;"
		(*strMap)['�']=","; // "&cedil;"
		(*strMap)['�']="^1"; // "&sup1;"
		(*strMap)['�']="_"; // "&frac14;"
		(*strMap)['�']="_"; // "&frac12;"
		(*strMap)['�']="_"; // "&frac34;"
		(*strMap)['�']="?"; // "&iquest;"
		(*strMap)['�']="A"; // "&Agrave;"
		(*strMap)['�']="A"; // "&Aacute;"
		(*strMap)['�']="A"; // "&Atilde;"
		(*strMap)['�']="A"; // "&Acirc;"
		(*strMap)['�']="Ae"; // "&AElig;"
		(*strMap)['�']="ae"; // "&aelig;"
		(*strMap)['�']="C"; // "&Ccedil;"
		(*strMap)['�']="E"; // "&Egrave;"
		(*strMap)['�']="E"; // "&Eacute;"
		(*strMap)['�']="E"; // "&Ecirc;"
		(*strMap)['�']="E"; // "&Euml;"
		(*strMap)['�']="I"; // "&Igrave;"
		(*strMap)['�']="I"; // "&Iacute;"
		(*strMap)['�']="I"; // "&Icirc;"
		(*strMap)['�']="I"; // "&Iuml;"
		(*strMap)['�']="D"; // "&ETH;"
		(*strMap)['�']="N"; // "&Ntilde;"
		(*strMap)['�']="O"; // "&Ograve;"
		(*strMap)['�']="O"; // "&Oacute;"
		(*strMap)['�']="O"; // "&Ocirc;"
		(*strMap)['�']="O"; // "&Otilde;"
		(*strMap)['�']="O"; // "&Oslash;"
		(*strMap)['�']="O"; // "&Ugrave;"
		(*strMap)['�']="U"; // "&Uacute;"
		(*strMap)['�']="U"; // "&Ucirc;"
		(*strMap)['�']="Y"; // "&Yacute;"
		(*strMap)['�']="[Thorn]"; // "&THORN;"
		(*strMap)['�']="a"; // "&agrave;"
		(*strMap)['�']="a"; // "&aacute;"
		(*strMap)['�']="a"; // "&acirc;"
		(*strMap)['�']="a"; // "&atilde;"
		(*strMap)['�']="a"; // "&aring;"
		(*strMap)['�']="c"; // "&ccedil;"
		(*strMap)['�']="e"; // "&egrave;"
		(*strMap)['�']="e"; // "&eacute;"
		(*strMap)['�']="e"; // "&ecirc;"
		(*strMap)['�']="e"; // "&euml;"
		(*strMap)['�']="i"; // "&igrave;"
		(*strMap)['�']="i"; // "&iacute;"
		(*strMap)['�']="i"; // "&icirc;"
		(*strMap)['�']="i"; // "&iuml;"
		(*strMap)['�']="_"; // "&eth;"
		(*strMap)['�']="n"; // "&ntilde;"
		(*strMap)['�']="o"; // "&ograve;"
		(*strMap)['�']="o"; // "&oacute;"
		(*strMap)['�']="o"; // "&ocirc;"
		(*strMap)['�']="o"; // "&otilde;"
		(*strMap)['�']="o"; // "&oslash;"
		(*strMap)['�']="u"; // "&ugrave;"
		(*strMap)['�']="u"; // "&uacute;"
		(*strMap)['�']="u"; // "&ucirc;"
		(*strMap)['�']="y"; // "&yacute;"
		(*strMap)['�']="[thorn]"; // "&thorn;"
		(*strMap)['�']="y"; // "&yuml;"
		(*strMap)['�']="[curren]"; // "&curren;"
		(*strMap)['�']="[Paragraph]"; // "&sect;"
	}
	if ( level > 1 )
	{
		(*strMap)['�']="Ae"; // "&Auml;"
		(*strMap)['�']="Oe"; // "&Ouml;"
		(*strMap)['�']="Ue"; // "&Uuml;"
		(*strMap)['�']="ae"; // "&auml;"
		(*strMap)['�']="oe"; // "&ouml;"
		(*strMap)['�']="ue"; // "&uuml;"
		(*strMap)['�']="ss"; // "&szlig;"
	}
	if (level >2)
	{
		(*strMap)['�']="(c)"; // "&copy;"
		(*strMap)['�']="(R)"; // "&reg;"
		(*strMap)['�']="[div]"; // "&divide;"
		(*strMap)['�']="[deg]"; // "&deg;"
		(*strMap)['&']="+"; // "&deg;"
	}

	if (level > 3)
	{
		(*strMap)[':']="_";
		(*strMap)['?']="[fz]";
		(*strMap)['!']="[az]";
		(*strMap)['�']="_"; // "&uml;"
		(*strMap)['\'']="_";
	}
	if (level > 4)
	{
		(*strMap)['/']="_"; // achtung!!  verzeichnisnamen wuerden hier zerlegt !
		(*strMap)['\\']="_"; // achtung!!  kann terminierte strings zerlegen !
	}
}

string Stringfixer::badC2Str(char c)
{
	if ( strMap->count(c) > 0 )
	#ifdef FIXER_STATS
	{ f++;
	#endif
		return strMap->find(c)->second;
	#ifdef FIXER_STATS
	}
	#endif
	else
	#ifdef FIXER_STATS
	{ i++;
	#endif
		return string(1, c);
	#ifdef FIXER_STATS
	}
	#endif
}

string Stringfixer::badC2Html(char c)
{
	if ( htmMap->count(c) > 0 )
	#ifdef FIXER_STATS
	{ f++;
	#endif
		return htmMap->find(c)->second;
	#ifdef FIXER_STATS
	}
	#endif
	else
	#ifdef FIXER_STATS
	{ i++;
	#endif
		return string(1, c);
	#ifdef FIXER_STATS
	}
	#endif
}

string Stringfixer::badStr2Str(string s)
{
	for ( cnt = 0; cnt < s.size(); cnt++ )
		s.replace(cnt, 1, badC2Str(s.at(cnt)));
	return s;
}
string Stringfixer::badStr2HtmlStr(string s)
{
	for ( cnt = 0; cnt < s.size(); cnt++ )
		s.replace(cnt, 1, badC2Html(s.at(cnt)));
	return s;
}

Stringfixer::~Stringfixer()
{
	#ifdef FIXER_STATS
	printf("#Stringfixer exit (%u fixed, %u ignored)\n", f, i);
	#endif
}



#endif

