      document.addEventListener('DOMContentLoaded', function() {
          document.querySelectorAll('a[data-bs-toggle="collapse"]').forEach(function(element) {
              element.addEventListener('click', function(e) {
                  var target = e.target.closest('[data-bs-toggle="collapse"]');
                  var icon = target.querySelector('i');
                  if (icon) {
                      icon.classList.toggle('fa-arrow-alt-circle-up');
                      icon.classList.toggle('fa-arrow-alt-circle-down');
                  }
              });
          });
          /** Add hash to the URL to support changing tab on page reload */
          var mainNav = document.querySelector('#mainNav');
          mainNav.addEventListener('click', function(e) {
              var target = e.target.closest('a');
              var href = target.getAttribute('href');
              var el = href ? document.querySelector(href) : false;
              if (el) {
                  window.location.hash = href.replace('#', '#!');
              }
          });
      
          /**
           * Check and activate tab content if the URL contains a valid tab ID (hash).
           * Tab is switched before Bootstrap is loaded.
           * */
          var hash = window.location.hash.toString().replace('#!', '#');
          var tabTriggerEl = mainNav.querySelector('a[href="' + hash + '"]');
          var tabContentEl = document.querySelector('#nav-tabContent');
          if (tabTriggerEl) {
              var activeLink = mainNav.querySelector('.nav-link.active');
              if (activeLink) {
                  activeLink.classList.remove('active');
              }
              var activePane = tabContentEl.querySelector('.tab-pane.active');
              activePane.classList.remove('active', 'show');
              tabTriggerEl.parentElement.classList.add('active');
      
              var newPane = tabContentEl.querySelector('.tab-pane' + hash);
              if (newPane) {
                  newPane.classList.add('active', 'show');
              }
              tabTriggerEl.classList.add('active');
          }
          
          
          // Listen for tab changes and update URL hash
          document.querySelectorAll('#mainNav a').forEach(function(tab) {
              tab.addEventListener('click', function(e) {
                  var hash = this.getAttribute('href');
                  window.location.hash = '!' + hash.replace('#', '');
              });
          });
          
          // Function to activate a tab based on the current URL hash, or a default tab if no hash
          function activateTabFromHash() {
              var hash = window.location.hash.replace('!', '');
              // Default to the main tab if no hash is present
              if (!hash) {
                  hash = '#research'; // Adjust this to match your default tab's href attribute value
              }
              
              var tab = document.querySelector(`#mainNav a[href="${hash}"]`);
              if (tab) {
                  new bootstrap.Tab(tab).show(); // Bootstrap's method to show the tab
              }
          }
          
          
          // Listen for hashchange events to support back/forward navigation
          window.addEventListener('hashchange', activateTabFromHash);
          
          // Activate tab from URL on page load
          activateTabFromHash();
          
      });
