---
title: Common Elements
weight: 1
---

# Common Elements

The site is based on the [Hugo framework](https://gohugo.io/), which allows to write pages with just `.md` (Markdown) files. All that it's needed is to have, at the beginning of each page, a `yaml` section which tells Hugo how to render the page. An example of page could be the following:

```yaml
---
title: Professors Offices
weight: 1
bookToc: true
---

# Professors Offices

Each professors has an office...

```

In that example, there are 3 elements:
 - `title`: represents the title of the page that will be shown in the left index;
 - `weight`: represents how much high in the index the page should be positioned (the lower the number, the higher the page);
 - `bookToc`: represents whether the page should have the table of contents on the right.
