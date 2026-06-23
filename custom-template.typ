$numbering.typ()$

$definitions.typ()$

$typst-template.typ()$

$for(header-includes)$
$header-includes$
$endfor$

$page.typ()$

#import "@preview/orange-book:0.7.1": book, part, chapter, appendices

#show: book.with(
$if(title)$
  title: [$title$],
$endif$
$if(subtitle)$
  subtitle: [$subtitle$],
$endif$
$if(by-author)$
  author: "$for(by-author)$$it.name.literal$$sep$, $endfor$",
$endif$
$if(date)$
  date: "$date$",
$endif$
$if(lang)$
  lang: "$lang$",
$endif$
  main-color: brand-color.at("primary", default: blue),
  font-size: 20pt,
  logo: {
    let logo-info = brand-logo.at("medium", default: none)
    if logo-info != none { image(logo-info.path, alt: logo-info.at("alt", default: none)) }
  },
$if(toc-depth)$
  outline-depth: $toc-depth$,
$endif$
$if(lof)$
  list-of-figure-title: "$if(crossref.lof-title)$$crossref.lof-title$$else$$crossref-lof-title$$endif$",
$endif$
$if(lot)$
  list-of-table-title: "$if(crossref.lot-title)$$crossref.lot-title$$else$$crossref-lot-title$$endif$",
$endif$
$if(margin-geometry)$
  padded-heading-number: false,
$endif$
)

$if(margin-geometry)$
// Configure marginalia page geometry for book context
#import "@preview/marginalia:0.3.1" as marginalia

#show: marginalia.setup.with(
  inner: (
    far: $margin-geometry.inner.far$,
    width: $margin-geometry.inner.width$,
    sep: $margin-geometry.inner.separation$,
  ),
  outer: (
    far: $margin-geometry.outer.far$,
    width: $margin-geometry.outer.width$,
    sep: $margin-geometry.outer.separation$,
  ),
  top: $if(margin.top)$$margin.top$$else$1.25in$endif$,
  bottom: $if(margin.bottom)$$margin.bottom$$else$1.25in$endif$,
  book: true,
  clearance: $margin-geometry.clearance$,
)
$endif$

$for(include-before)$
$include-before$
$endfor$

$body$

$notes.typ()$
$biblio.typ()$

$for(include-after)$
$include-after$
$endfor$
