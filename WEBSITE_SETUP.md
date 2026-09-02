# Website setup — plain-English steps

You own **giv-theory.com** and **giv-theory.org** at **Namecheap** (paid to Jan
2027). Neither points anywhere yet — they show Namecheap's default *parking
page*, which is normal and means "empty lot, nothing built here yet." Nothing is
broken; nothing is out of date. This file turns that empty lot into your site.

Do it in two stages. Stage 1 gets a working site for free. Stage 2 puts your
pretty domain on it. You can stop after Stage 1 and still have a live website.

---

## Stage 1 — turn the free GitHub site on

1. Go to the repo on GitHub → **Settings** (top tab) → **Pages** (left sidebar).
2. Under **Build and deployment → Source**, choose **Deploy from a branch**.
3. **Branch:** pick `master` (after the pull requests are merged) → **Folder:**
   `/(root)` → **Save**.
4. Wait ~1 minute, refresh the page. GitHub shows a green banner with your live
   URL, roughly: **https://kekekatie.github.io/geometric-impedance/**

That's a real, current website. You can share that link as-is.

---

## Stage 2 — put giv-theory.com on it

You'll touch two places: Namecheap (to aim the domain) and GitHub (to accept it).

### In Namecheap
1. **Domain List** → **Manage** next to `giv-theory.com` → **Advanced DNS** tab.
2. **Delete** the default parking records — usually a `CNAME` record for `www`
   pointing at a parking page, and/or a "URL Redirect" record on `@`. (If unsure,
   delete any record that mentions "parkingpage" or "redirect." You can't
   permanently break anything here; records can be re-added.)
3. **Add these five records** (Type · Host · Value · TTL Automatic):

   | Type | Host | Value |
   |---|---|---|
   | A Record | @ | `185.199.108.153` |
   | A Record | @ | `185.199.109.153` |
   | A Record | @ | `185.199.110.153` |
   | A Record | @ | `185.199.111.153` |
   | CNAME Record | www | `kekekatie.github.io.` |

   (Those four IPs are GitHub Pages' official addresses — the same for everyone.
   Keep the trailing dot on the CNAME value.)

### In GitHub
4. Repo → **Settings → Pages → Custom domain** → type `giv-theory.com` → **Save**.
   (This automatically adds a small `CNAME` file to the repo — that's expected.)
5. Wait. DNS can take anywhere from a few minutes to a few hours to propagate.
6. When the box stops saying "checking," tick **Enforce HTTPS** so the site
   loads securely (the padlock). This can take up to a day to become available —
   just check back.

Done. `https://giv-theory.com` now serves your site.

### The .org (optional)
To make `giv-theory.org` also lead to the site, the simplest route is a
**redirect**: Namecheap → Manage `giv-theory.org` → set a **URL Redirect** record
on `@` (and `www`) pointing to `https://giv-theory.com`. That way one domain is
the "real" site and the other just forwards to it.

---

## If something looks stuck
- "There's already a site registered" on Namecheap = the parking page. Normal
  until Stage 2 is done.
- GitHub says "domain does not resolve to the GitHub Pages server" = DNS hasn't
  propagated yet, or an A record has a typo. Wait, then re-check the five records.
- Still stuck? Bring the exact on-screen message back here and we'll fix it
  step by step.
