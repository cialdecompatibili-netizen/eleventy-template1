---
layout: blog.njk
title: Articoli
date: 2017-01-01
pagination:
  data: collections.post
  size: 20
permalink: "blog{% if pagination.pageNumber > 0 %}/page/{{ pagination.pageNumber }}{% endif %}/index.html"
metaDescription: Una pagina Blog di esempio che elenca vari articoli.
subtitle: Una raccolta di articoli tecnici e pensieri sparsi
eleventyNavigation:
  key: Blog
  order: 2
---
