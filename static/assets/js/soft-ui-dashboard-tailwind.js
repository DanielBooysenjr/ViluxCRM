var page = window.location.pathname.split("/").pop().split(".")[0];
var aux = window.location.pathname.split("/");
var to_build = (aux.includes('pages') ? '../' : './');
var root = window.location.pathname.split("/");

if (!aux.includes("pages")) {
  page = "dashboard";
}

var staticPath = (aux.includes('pages') ? '../../' : '../');

// loadStylesheet(staticPath + "static/assets/css/perfect-scrollbar.css");
// loadJS(staticPath + "static/assets/js/perfect-scrollbar.js", true);

if (document.querySelector("nav [navbar-trigger]")) {
  loadJS(staticPath + "static/assets/js/navbar-collapse.js", true);
}

if (document.querySelector("[data-target='tooltip']")) {
  loadJS(staticPath + "static/assets/js/tooltips.js", true);
  loadStylesheet(staticPath + "static/assets/css/tooltips.css");
}

if (document.querySelector("[nav-pills]")) {
  loadJS(staticPath + "static/assets/js/nav-pills.js", true);
}

if (document.querySelector("[dropdown-trigger]")) {
  loadJS(staticPath + "static/assets/js/dropdown.js", true);
}

if (document.querySelector("[fixed-plugin]")) {
  loadJS(staticPath + "static/assets/js/fixed-plugin.js", true);
}

if (document.querySelector("[navbar-main]")) {
  loadJS(staticPath + "static/assets/js/sidenav-burger.js", true);
  loadJS(staticPath + "static/assets/js/navbar-sticky.js", true);
}

if (document.querySelector("canvas")) {
  loadJS(staticPath + "static/assets/js/chart-1.js", true);
  loadJS(staticPath + "static/assets/js/chart-2.js", true);
}

function loadJS(FILE_URL, async) {
  let dynamicScript = document.createElement("script");

  dynamicScript.setAttribute("src", FILE_URL);
  dynamicScript.setAttribute("type", "text/javascript");
  dynamicScript.setAttribute("async", async);

  document.head.appendChild(dynamicScript);
}

function loadStylesheet(FILE_URL) {
  let dynamicStylesheet = document.createElement("link");

  dynamicStylesheet.setAttribute("href", FILE_URL);
  dynamicStylesheet.setAttribute("type", "text/css");
  dynamicStylesheet.setAttribute("rel", "stylesheet");

  document.head.appendChild(dynamicStylesheet);
}
