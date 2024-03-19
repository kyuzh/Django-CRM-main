// Fonction pour rafraîchir la page en fonction du nombre d'éléments par page
function refreshPage_elements() {
  // Récupérez la valeur actuelle de "start" depuis l'URL
  var urlParams = new URLSearchParams(window.location.search);
  var page = parseInt(urlParams.get("page")) || 1;
  var elementsPerPage = parseInt(document.getElementById("elementsPerPage").value) || 10;
  var start = (page - 1) * elementsPerPage || 0;
  var end = page * elementsPerPage - 1; // Calcul de la valeur de "end"
  var searchInput = document.querySelector('input[name="searchValue"]');
  var searchValue = searchInput.value.toUpperCase();

  if (page <= 0) {
    page = 1;
    start = 0;
    end = elementsPerPage - 1;
  }

  // Mettre à jour les valeurs des paramètres dans l'URL
  urlParams.set("page", page.toString());
  urlParams.set("elementsPerPage", elementsPerPage.toString());
  urlParams.set("searchValue", searchValue.toString());

  // Sauvegarder dans le stockage local
  localStorage.setItem("searchValue", searchValue);
  // Enregistrez également le nombre choisi dans le stockage local
  localStorage.setItem("elementsPerPage", elementsPerPage);

  // Rediriger vers la nouvelle URL avec les paramètres mis à jour
  window.location.href = "?" + urlParams.toString();
}

// Lorsque la page est chargée, vérifiez s'il y a une valeur dans le stockage local pour "elementsPerPage"
// Si c'est le cas, configurez l'élément de sélection avec cette valeur
document.addEventListener("DOMContentLoaded", function () {
  var elementsPerPage_input = document.getElementById('elementsPerPage');
  if (elementsPerPage_input) {
      var elementsPerPage = localStorage.getItem("elementsPerPage");
      if (elementsPerPage !== null) {
        document.getElementById("elementsPerPage").value = elementsPerPage;
        console.log("Valeur de elementsPerPage mise à jour dans l'élément de sélection : " + elementsPerPage);
      }

      var searchInput = document.querySelector('input[name="searchValue"]');
      var searchValue = searchInput.value.toUpperCase();

      if (searchValue !== null) {
        document.querySelector('input[name="searchValue"]').value = searchValue;
        console.log("Valeur de searchValue mise à jour : " + searchValue);
      }

      // Récupérez la valeur actuelle de "start" depuis l'URL
        var urlParams = new URLSearchParams(window.location.search);
        var page = parseInt(urlParams.get("page")) || 1;
        var elementsPerPage = parseInt(document.getElementById("elementsPerPage").value) || 10;
        var start = (page - 1) * elementsPerPage || 0;
        var end = page * elementsPerPage - 1; // Calcul de la valeur de "end"

        var leadElement = document.querySelector('.lead');
        var leadText = leadElement.textContent;
        var totalItems = parseInt(leadText.match(/\d+/)[0]) - 1;

        if ((page - 1) * elementsPerPage > totalItems) {
          page = page - 1;
          end = totalItems;
          start = Math.max(0, end - end % elementsPerPage);
        }

        var tableRows = document.querySelectorAll('.table tbody tr');
        for (var i = 0; i < tableRows.length; i++) {
          if (i >= start && i < end + 1) {
            console.log(tableRows[i]);
            tableRows[i].style.display = 'table-row';
          } else {
            tableRows[i].style.display = 'none';
          }
        }

        // Mettre à jour les valeurs des paramètres dans l'URL
        urlParams.set("page", page.toString());
        urlParams.set("elementsPerPage", elementsPerPage.toString());

        // Check if the "table" parameter is present and add it to the URL
        var tableParam = urlParams.get("table");
        if (tableParam !== null) {
          urlParams.set("table", tableParam);
        }

        // Attachez la fonction refreshPage_elements à l'événement "change" de l'élément avec l'ID "elementsPerPage"
        document.getElementById("elementsPerPage").addEventListener("change", refreshPage_elements);

}
});


// cliquer sur le bouton "recherche"
document.addEventListener("DOMContentLoaded", function () {
  var searchButton = document.getElementById('searchButton');
  if (searchButton) {
    searchButton.addEventListener('click', function (event) {
    // Récupérez l'élément <p> avec l'ID "recordCount"
      var nouveauRecordCount = 0;

      var urlParams = new URLSearchParams(window.location.search);
      var page = parseInt(urlParams.get("page")) || 1;
      var elementsPerPage = parseInt(document.getElementById("elementsPerPage").value) || 10;
      var start = (page - 1) * elementsPerPage || 0;
      var end = page * elementsPerPage - 1; // Calcul de la valeur de "end"
      var searchInput = document.querySelector('input[name="searchValue"]');
      var searchValue = searchInput.value.toUpperCase();

      start = 0;
      end = elementsPerPage - 1;
      var tableName = urlParams.get('table');

      // Parcourez les éléments du tableau correspondant à la table spécifiée dans l'URL
      var tableRows = document.querySelectorAll('.' + tableName + ' tbody tr');

      console.log(tableRows);
      for (var i = 0; i < tableRows.length; i++) {
        var row = tableRows[i];
        console.log(row);
        var phoneValue = row.querySelector('td:nth-child(3)').textContent.toUpperCase(); // Utilisez le numéro de colonne correspondant à "Phone" (dans cet exemple, c'est la 3e colonne)
        var addressValue = row.querySelector('td:nth-child(4)').textContent.toUpperCase(); // Utilisez le numéro de colonne correspondant à "Phone" (dans cet exemple, c'est la 3e colonne)

        // Comparez la valeur de recherche avec les valeurs des colonnes "Phone" et "Address"
        if (phoneValue.includes(searchValue) || addressValue.includes(searchValue)) {
          // Affichez la ligne si elle correspond au filtre
          row.style.display = 'table-row';
          nouveauRecordCount = nouveauRecordCount + 1;
        } else {
          // Masquez la ligne si elle ne correspond pas au filtre
          row.style.display = 'none';
        }
        // Récupérez l'élément <p> avec l'ID "recordCount"
        var recordCountElement = document.getElementById('recordCount');

        // Mettez à jour le contenu de l'élément <p> avec la nouvelle valeur
        recordCountElement.textContent = 'Total: ' + nouveauRecordCount; // Remplacez 'nouveauRecordCount' par la nouvelle valeur souhaitée


        // Mettre à jour les valeurs des paramètres dans l'URL
        urlParams.set("page", page.toString());
        urlParams.set("elementsPerPage", elementsPerPage.toString());

        // Check if the "table" parameter is present and add it to the URL
        var tableParam = urlParams.get("table");
        if (tableParam !== null) {
          urlParams.set("table", tableParam);
        }

        urlParams.set("searchValue", searchValue.toString());
        // Rediriger vers la nouvelle URL avec les paramètres mis à jour
        window.location.href = "?" + urlParams.toString();

        // Sauvegarder dans le stockage local
        localStorage.setItem("searchValue", searchValue);
      }
    });
  }
});



// Fonction pour changer de page
function updateParams(change) {
  var urlParams = new URLSearchParams(window.location.search);
  var page = parseInt(urlParams.get("page")) || 1;
  var elementsPerPage = parseInt(document.getElementById("elementsPerPage").value) || 10;
  var start = (page - 1) * elementsPerPage || 0;
  var end = page * elementsPerPage - 1; // Calcul de la valeur de "end"
  var searchInput = document.querySelector('input[name="searchValue"]');
  var searchValue = searchInput.value.toUpperCase();

  page = page + change
  change = change * elementsPerPage
  start += change;
  var end = start + elementsPerPage -1 ;

  if (page <= 0) {
    page = 1;
    start = 0;
    end = elementsPerPage - 1;
  }

  // Obtenez le nombre total d'éléments à partir de l'élément HTML avec la classe "lead"
  var leadElement = document.querySelector('.lead');
  var leadText = leadElement.textContent;
  var totalItems = parseInt(leadText.match(/\d+/)[0]) - 1;

  if ((page-1) * elementsPerPage  > totalItems) {
    page = page - 1
    end = totalItems;
    start = Math.max(0,end - end % elementsPerPage);
  }
  // Mettre à jour les valeurs des paramètres dans l'URL
  urlParams.set("page", page.toString());
  urlParams.set("elementsPerPage", elementsPerPage.toString());

  // Check if the "table" parameter is present and add it to the URL
  var tableParam = urlParams.get("table");
  if (tableParam !== null) {
    urlParams.set("table", tableParam);
  }

  urlParams.set("searchValue", searchValue.toString());
  // Rediriger vers la nouvelle URL avec les paramètres mis à jour
  window.location.href = "?" + urlParams.toString();


  // Désactiver le lien "Next" s'il n'y a plus d'éléments suivants
  if (page * elementsPerPage >= totalItems) {
    document.getElementById("next-link").style.pointerEvents = "none";
  } else {
    // Activer le lien "Next" s'il y a des éléments suivants
    document.getElementById("next-link").style.pointerEvents = "auto";
  }
  // Désactiver le lien "Previous" s'il n'y a plus d'éléments précédents
  if (start <= 0) {
    document.getElementById("previous-link").style.pointerEvents = "none";
  } else {
    // Activer le lien "Previous" s'il y a des éléments précédents
    document.getElementById("previous-link").style.pointerEvents = "auto";
  }

}

function goToPage() {
    var pageNumberInput = document.getElementById("pageNumberInput").value;
    var pageNumber = parseInt(pageNumberInput);

    // Récupérer la valeur de recherche depuis le champ "Recherche"
    var searchInput = document.querySelector('input[name="searchValue"]');
    // Vérifiez si le champ de recherche est vide
    var searchValue = searchInput.value.trim().toUpperCase();

    if (searchValue === "") {
        // Si le champ est vide, utilisez la valeur de searchValue à partir des paramètres d'URL
        var urlParams = new URLSearchParams(window.location.search);
        searchValue = urlParams.get("searchValue") || ""; // Utilisez une valeur par défaut si la valeur n'est pas présente
    }

    // Obtenez le nombre total d'éléments à partir de l'élément HTML avec la classe "lead"
    var leadElement = document.querySelector('.lead');
    var leadText = leadElement.textContent;
    var totalItems = parseInt(leadText.match(/\d+/)[0]) - 1;

    var elementsPerPage = parseInt(document.getElementById("elementsPerPage").value) || 10;
    var start = (pageNumber - 1) * elementsPerPage || 0;
    var end = start + elementsPerPage - 1;

    if (end > totalItems) {
        end = totalItems;
    }

    if (!isNaN(pageNumber) && pageNumber >= 1) {
        // Mettre à jour les valeurs des paramètres dans l'URL
        var urlParams = new URLSearchParams(window.location.search);
        urlParams.set("elementsPerPage", elementsPerPage.toString());

        // Check if the "table" parameter is present and add it to the URL
        var tableParam = urlParams.get("table");
        if (tableParam) {
            urlParams.set("table", tableParam);
        }

        urlParams.set("searchValue", searchValue);
        localStorage.setItem("searchValue", searchValue); // Sauvegarder dans le stockage local

        // Mettre à jour le paramètre de la page dans l'URL
        urlParams.set("page", pageNumber.toString());

        // Rediriger vers la nouvelle URL avec les paramètres mis à jour
        window.location.href = "?" + urlParams.toString();
        console.log(window.location.href);
    }
}

// script pour récupérer la valeur de la page depuis l'URL
document.addEventListener("DOMContentLoaded", function () {
    // Récupérer les paramètres de l'URL
    var urlParams = new URLSearchParams(window.location.search);

    // Récupérer la valeur de la page à partir des paramètres de l'URL
    var pageNumberFromUrl = urlParams.get("page");

    // Mettre à jour le champ de saisie de numéro de page
    var pageNumberInput = document.getElementById("pageNumberInput");
    if (pageNumberFromUrl !== null && !isNaN(pageNumberFromUrl) && parseInt(pageNumberFromUrl) > 0) {
        pageNumberInput.value = pageNumberFromUrl;
    }
});
