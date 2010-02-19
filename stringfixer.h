/*
 *  ##############################
 *  #        stringfixer.h       #
 *  #                            #
 *  #            2008 (c) Psyjo© #
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
	(*htmMap)['¡']="&iexcl;";
	(*htmMap)['¢']="&cent;";
	(*htmMap)['£']="&pound;";
	(*htmMap)['¤']="&curren;";
	(*htmMap)['¥']="&yen;";
	(*htmMap)['¦']="&brvbar;";
	(*htmMap)['§']="&sect;";
	(*htmMap)['¨']="&uml;";
	(*htmMap)['©']="&copy;";
	(*htmMap)['ª']="&ordf;";
	(*htmMap)['«']="&laquo;";
	(*htmMap)['¬']="&not;";
	(*htmMap)['®']="&reg;";
	(*htmMap)['¯']="&macr;";
	(*htmMap)['°']="&deg;";
	(*htmMap)['±']="&plusmn;";
	(*htmMap)['²']="&sup2;";
	(*htmMap)['³']="&sup3;";
	(*htmMap)['´']="&acute;";
	(*htmMap)['µ']="&micro;";
	(*htmMap)['¶']="&para;";
	(*htmMap)['·']="&middot;";
	(*htmMap)['¸']="&cedil;";
	(*htmMap)['¹']="&sup1;";
	(*htmMap)['º']="&ordm;";
	(*htmMap)['»']="&raquo;";
	(*htmMap)['¼']="&frac14;";
	(*htmMap)['½']="&frac12;";
	(*htmMap)['¾']="&frac34;";
	(*htmMap)['¿']="&iquest;";
	(*htmMap)['À']="&Agrave;";
	(*htmMap)['Á']="&Aacute;";
	(*htmMap)['Ã']="&Atilde;";
	(*htmMap)['Â']="&Acirc;";
	(*htmMap)['Ä']="&Auml;";
	(*htmMap)['Æ']="&AElig;";
	(*htmMap)['Ç']="&Ccedil;";
	(*htmMap)['È']="&Egrave;";
	(*htmMap)['É']="&Eacute;";
	(*htmMap)['Ê']="&Ecirc;";
	(*htmMap)['Ë']="&Euml;";
	(*htmMap)['Ì']="&Igrave;";
	(*htmMap)['Í']="&Iacute;";
	(*htmMap)['Î']="&Icirc;";
	(*htmMap)['Ï']="&Iuml;";
	(*htmMap)['Ð']="&ETH;";
	(*htmMap)['Ñ']="&Ntilde;";
	(*htmMap)['Ò']="&Ograve;";
	(*htmMap)['Ó']="&Oacute;";
	(*htmMap)['Ô']="&Ocirc;";
	(*htmMap)['Õ']="&Otilde;";
	(*htmMap)['Ö']="&Ouml;";
	(*htmMap)['×']="&times;";
	(*htmMap)['Ø']="&Oslash;";
	(*htmMap)['Ù']="&Ugrave;";
	(*htmMap)['Ú']="&Uacute;";
	(*htmMap)['Û']="&Ucirc;";
	(*htmMap)['Ü']="&Uuml;";
	(*htmMap)['Ý']="&Yacute;";
	(*htmMap)['Þ']="&THORN;";
	(*htmMap)['ß']="&szlig;";
	(*htmMap)['à']="&agrave;";
	(*htmMap)['á']="&aacute;";
	(*htmMap)['â']="&acirc;";
	(*htmMap)['ã']="&atilde;";
	(*htmMap)['ä']="&auml;";
	(*htmMap)['å']="&aring;";
	(*htmMap)['æ']="&aelig;";
	(*htmMap)['ç']="&ccedil;";
	(*htmMap)['è']="&egrave;";
	(*htmMap)['é']="&eacute;";
	(*htmMap)['ê']="&ecirc;";
	(*htmMap)['ë']="&euml;";
	(*htmMap)['ì']="&igrave;";
	(*htmMap)['í']="&iacute;";
	(*htmMap)['î']="&icirc;";
	(*htmMap)['ï']="&iuml;";
	(*htmMap)['ð']="&eth;";
	(*htmMap)['ñ']="&ntilde;";
	(*htmMap)['ò']="&ograve;";
	(*htmMap)['ó']="&oacute;";
	(*htmMap)['ô']="&ocirc;";
	(*htmMap)['õ']="&otilde;";
	(*htmMap)['ö']="&ouml;";
	(*htmMap)['÷']="&divide;";
	(*htmMap)['ø']="&oslash;";
	(*htmMap)['ù']="&ugrave;";
	(*htmMap)['ú']="&uacute;";
	(*htmMap)['û']="&ucirc;";
	(*htmMap)['ü']="&uuml;";
	(*htmMap)['ý']="&yacute;";
	(*htmMap)['þ']="&thorn;";
	(*htmMap)['ÿ']="&yuml;";


	if ( spacelevel > 0 )
		(*strMap)[' ']="_"; // "&nbsp;"
	
	if (level > 0)
	{
		(*strMap)['¡']="i"; // "&iexcl;"
		(*strMap)['¢']="c"; // "&cent;"
		(*strMap)['£']="[Pfund]"; // "&pound;"
		(*strMap)['¥']="[Yen]"; // "&yen;"
		(*strMap)['¦']="|"; // "&brvbar;"
		(*strMap)['ª']="_"; // "&ordf;"
		(*strMap)['º']="_"; // "&ordm;"
		(*strMap)['«']="<<"; // "&laquo;"
		(*strMap)['»']=">>"; // "&raquo;"
		(*strMap)['¬']="_"; // "&not;"
		(*strMap)['¯']="-"; // "&macr;"
		(*strMap)['±']="+-"; // "&plusmn;"
		(*strMap)['×']="x"; // "&times;"
		(*strMap)['²']="^2"; // "&sup2;"
		(*strMap)['³']="^3"; // "&sup3;"
		(*strMap)['´']="_"; // "&acute;"
		(*strMap)['µ']="[mu]"; // "&micro;"
		(*strMap)['¶']="_"; // "&para;"
		(*strMap)['·']="-"; // "&middot;"
		(*strMap)['¸']=","; // "&cedil;"
		(*strMap)['¹']="^1"; // "&sup1;"
		(*strMap)['¼']="_"; // "&frac14;"
		(*strMap)['½']="_"; // "&frac12;"
		(*strMap)['¾']="_"; // "&frac34;"
		(*strMap)['¿']="?"; // "&iquest;"
		(*strMap)['À']="A"; // "&Agrave;"
		(*strMap)['Á']="A"; // "&Aacute;"
		(*strMap)['Ã']="A"; // "&Atilde;"
		(*strMap)['Â']="A"; // "&Acirc;"
		(*strMap)['Æ']="Ae"; // "&AElig;"
		(*strMap)['æ']="ae"; // "&aelig;"
		(*strMap)['Ç']="C"; // "&Ccedil;"
		(*strMap)['È']="E"; // "&Egrave;"
		(*strMap)['É']="E"; // "&Eacute;"
		(*strMap)['Ê']="E"; // "&Ecirc;"
		(*strMap)['Ë']="E"; // "&Euml;"
		(*strMap)['Ì']="I"; // "&Igrave;"
		(*strMap)['Í']="I"; // "&Iacute;"
		(*strMap)['Î']="I"; // "&Icirc;"
		(*strMap)['Ï']="I"; // "&Iuml;"
		(*strMap)['Ð']="D"; // "&ETH;"
		(*strMap)['Ñ']="N"; // "&Ntilde;"
		(*strMap)['Ò']="O"; // "&Ograve;"
		(*strMap)['Ó']="O"; // "&Oacute;"
		(*strMap)['Ô']="O"; // "&Ocirc;"
		(*strMap)['Õ']="O"; // "&Otilde;"
		(*strMap)['Ø']="O"; // "&Oslash;"
		(*strMap)['Ù']="O"; // "&Ugrave;"
		(*strMap)['Ú']="U"; // "&Uacute;"
		(*strMap)['Û']="U"; // "&Ucirc;"
		(*strMap)['Ý']="Y"; // "&Yacute;"
		(*strMap)['Þ']="[Thorn]"; // "&THORN;"
		(*strMap)['à']="a"; // "&agrave;"
		(*strMap)['á']="a"; // "&aacute;"
		(*strMap)['â']="a"; // "&acirc;"
		(*strMap)['ã']="a"; // "&atilde;"
		(*strMap)['å']="a"; // "&aring;"
		(*strMap)['ç']="c"; // "&ccedil;"
		(*strMap)['è']="e"; // "&egrave;"
		(*strMap)['é']="e"; // "&eacute;"
		(*strMap)['ê']="e"; // "&ecirc;"
		(*strMap)['ë']="e"; // "&euml;"
		(*strMap)['ì']="i"; // "&igrave;"
		(*strMap)['í']="i"; // "&iacute;"
		(*strMap)['î']="i"; // "&icirc;"
		(*strMap)['ï']="i"; // "&iuml;"
		(*strMap)['ð']="_"; // "&eth;"
		(*strMap)['ñ']="n"; // "&ntilde;"
		(*strMap)['ò']="o"; // "&ograve;"
		(*strMap)['ó']="o"; // "&oacute;"
		(*strMap)['ô']="o"; // "&ocirc;"
		(*strMap)['õ']="o"; // "&otilde;"
		(*strMap)['ø']="o"; // "&oslash;"
		(*strMap)['ù']="u"; // "&ugrave;"
		(*strMap)['ú']="u"; // "&uacute;"
		(*strMap)['û']="u"; // "&ucirc;"
		(*strMap)['ý']="y"; // "&yacute;"
		(*strMap)['þ']="[thorn]"; // "&thorn;"
		(*strMap)['ÿ']="y"; // "&yuml;"
		(*strMap)['¤']="[curren]"; // "&curren;"
		(*strMap)['§']="[Paragraph]"; // "&sect;"
	}
	if ( level > 1 )
	{
		(*strMap)['Ä']="Ae"; // "&Auml;"
		(*strMap)['Ö']="Oe"; // "&Ouml;"
		(*strMap)['Ü']="Ue"; // "&Uuml;"
		(*strMap)['ä']="ae"; // "&auml;"
		(*strMap)['ö']="oe"; // "&ouml;"
		(*strMap)['ü']="ue"; // "&uuml;"
		(*strMap)['ß']="ss"; // "&szlig;"
	}
	if (level >2)
	{
		(*strMap)['©']="(c)"; // "&copy;"
		(*strMap)['®']="(R)"; // "&reg;"
		(*strMap)['÷']="[div]"; // "&divide;"
		(*strMap)['°']="[deg]"; // "&deg;"
		(*strMap)['&']="+"; // "&deg;"
	}

	if (level > 3)
	{
		(*strMap)[':']="_";
		(*strMap)['?']="[fz]";
		(*strMap)['!']="[az]";
		(*strMap)['¨']="_"; // "&uml;"
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

