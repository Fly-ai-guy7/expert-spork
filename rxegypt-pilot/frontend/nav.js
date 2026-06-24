/* RxEgypt — shared product navigation.
 *
 * Injects a single, consistent top nav across all suite pages so the patient
 * app, Dawai, POS and Admin are no longer disconnected islands. The active
 * link is derived from the current filename. No dependencies; safe to include
 * on any page (it inserts itself at the top of <body> on DOMContentLoaded).
 *
 * 🌿 ✦ ASTRA INTELLIGENCE SERVICES ✦ 🌿 | ⚜ MISR ⚜
 */
(function () {
  var PAGES = [
    { file: "index.html", label: "Patient" },
    { file: "dawai-patient.html", label: "Dawai" },
    { file: "pharmacy-pos.html", label: "POS" },
    { file: "admin.html", label: "Admin" }
  ];

  function currentFile() {
    var path = window.location.pathname;
    var file = path.substring(path.lastIndexOf("/") + 1);
    return file === "" ? "index.html" : file;
  }

  function build() {
    var here = currentFile();
    var nav = document.createElement("nav");
    nav.className = "appnav";

    var brand = document.createElement("a");
    brand.className = "appnav-brand";
    brand.href = "index.html";
    brand.textContent = "🌿 RxEgypt";
    nav.appendChild(brand);

    var links = document.createElement("div");
    links.className = "appnav-links";
    PAGES.forEach(function (p) {
      var a = document.createElement("a");
      a.href = p.file;
      a.textContent = p.label;
      if (p.file === here) a.className = "active";
      links.appendChild(a);
    });
    nav.appendChild(links);

    document.body.insertBefore(nav, document.body.firstChild);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", build);
  } else {
    build();
  }
})();
