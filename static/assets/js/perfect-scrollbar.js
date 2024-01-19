(function () {
  var isWindows = navigator.platform.indexOf("Win") > -1 ? true : false;

  if (isWindows) {
    // Activate the PerfectScrollbar function on main panel
    if (document.querySelector("main")) {
      var mainpanel = document.querySelector("main");
      var psMain = new PerfectScrollbar(mainpanel);
    }

    // Create an array to store instances of PerfectScrollbar
    var psArray = [];

    // Iterate over elements with class "overflow-auto"
    if (document.querySelectorAll(".overflow-auto")) {
      var sidebarOverflowAuto = document.querySelectorAll(".overflow-auto");
      sidebarOverflowAuto.forEach((element) => {
        psArray.push(new PerfectScrollbar(element));
      });
    }

    // Iterate over elements with class "overflow-y-auto"
    if (document.querySelectorAll(".overflow-y-auto")) {
      var sidebarOverflowYAuto = document.querySelectorAll(".overflow-y-auto");
      sidebarOverflowYAuto.forEach((element) => {
        psArray.push(new PerfectScrollbar(element));
      });
    }

    // Iterate over elements with class "overflow-x-auto"
    if (document.querySelectorAll(".overflow-x-auto")) {
      var sidebarOverflowXAuto = document.querySelectorAll(".overflow-x-auto");
      sidebarOverflowXAuto.forEach((element) => {
        psArray.push(new PerfectScrollbar(element));
      });
    }
  }
})();
