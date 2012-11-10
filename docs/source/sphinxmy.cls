%
% sphinxhowto.cls for Sphinx (http://sphinx.pocoo.org/)
%

\NeedsTeXFormat{LaTeX2e}[1995/12/01]
\ProvidesClass{sphinxmy}[2012/11/10 Document class (Sphinx)]

% 'oneside' option overriding the 'twoside' default
\newif\if@oneside
\DeclareOption{oneside}{\@onesidetrue}
% Pass remaining document options to the parent class.
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{\sphinxdocclass}}
\ProcessOptions\relax

% Default to two-side document
\if@oneside
% nothing to do (oneside is the default)
\else
\PassOptionsToClass{twoside}{\sphinxdocclass}
\fi

\LoadClass{\sphinxdocclass}


% Set some sane defaults for section numbering depth and TOC depth.  You can
% reset these counters in your preamble.
%
\setcounter{secnumdepth}{2}

% Change the title page to look a bit better, and fit in with the fncychap
% ``Bjarne'' style a bit better.
%
\usepackage{textcase}
\renewcommand{\contentsname}{}

\newcommand{\mauthor}{}
\newcommand{\mtitle}{}
\newcommand{\mhead}{}
\newcommand{\mfoot}{}
\newcommand{\mflushtext}{}

\renewcommand{\maketitle}{
  \begin{titlepage}
    \let\footnotesize\small
    \let\footnoterule\relax
    \rule{\textwidth}{1pt}

    \ifsphinxpdfoutput
      \begingroup
      \def\\{, }
      \def\and{and }
      \pdfinfo{
        /Author (\mauthor)
        /Title (\mtitle)
      }
      \endgroup
    \fi
    
    {\large\centering{ \mhead } \par}%
    \rule{\textwidth}{1pt}
    \vfill
    {\Huge\centering \mtitle \par}%
    \vfill
    \begin{flushright}
        \normalsize{\mflushtext }
    \end{flushright}
    \vfill
    \centering{\mfoot}
  \end{titlepage}
  \cleardoublepage
  \setcounter{footnote}{0}%
  \let\thanks\relax\let\maketitle\relax
}

\newcommand{\mycontentsname}{}

\let\py@OldTableofcontents=\tableofcontents
\renewcommand{\tableofcontents}{%
  \setcounter{page}{1}%
  \pagebreak%
  \renewcommand{\contentsname}{\mycontentsname}
  \pagestyle{plain}%
  {%
    \parskip = 0mm%
    \py@OldTableofcontents%
    \if@openright%
      \ifodd\value{page}%
        \typeout{Adding blank page after the table of contents.}%
        \pagebreak\hspace{0pt}%
      \fi%
    \fi%
    \cleardoublepage%
  }%
  \pagenumbering{arabic}%
  \@ifundefined{fancyhf}{}{\pagestyle{normal}}%
}


\@ifundefined{fancyhf}{
  \pagestyle{plain}}{
  \pagestyle{normal}}		% start this way; change for
\pagenumbering{arabic}		% ToC & chapters

\thispagestyle{empty}

% Fix the bibliography environment to add an entry to the Table of
% Contents.
% For an article document class this environment is a section,
% so no page break before it.
\let\py@OldThebibliography=\thebibliography
\renewcommand{\thebibliography}[1]{
  \phantomsection
  \py@OldThebibliography{#1}
  \addcontentsline{toc}{section}{\bibname}
}

\newcommand{\npartname}{}

\def\@part[#1]#2{%
    \ifnum \c@secnumdepth >-2\relax
      \refstepcounter{part}%
      \addcontentsline{toc}{part}{\thepart\hspace{1em}#1}%
    \else
      \addcontentsline{toc}{part}{#1}%
    \fi
    \markboth{}{}%
    {\centering
     \interlinepenalty \@M
     \normalfont
     \ifnum \c@secnumdepth >-2\relax
       \huge\bfseries \npartname\nobreakspace\thepart
       \par
       \vskip 20\p@
     \fi
     \Huge \bfseries #2\par}%
    \@endpart}