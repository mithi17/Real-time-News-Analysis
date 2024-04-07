jQuery(document).ready(function($) {
    // Your jQuery code here
    $('#searchForm').submit(function(event) {
        event.preventDefault();
        var keyword = $('#keyword').val().trim();
        console.log(keyword);

        $.ajax({
            url: '/search',
            type: 'POST',
            data: { keyword: keyword },
            success: function(response) {
                displaySearchResults(response);
            },
            error: function(xhr, status, error) {
                console.error('Error:', error);
            }
        });
    });

    function displaySearchResults(results) {
        var searchResultsDiv = $('#searchResults');
        searchResultsDiv.empty(); // Clear previous results

        var count = results.length; // Count the number of articles

        // Count unique domains
        var uniqueDomains = {};
        for (var i = 0; i < count; i++) {
            var domain = getDomain(results[i].url);
            uniqueDomains[domain] = true;

            // Extract and print date and time
            // var updatedOn = results[i].updated_on;
            // var dateRange = formatDate(updatedOn);

            // console.log("Date and Time from Result:", dateRange);
            // console.log("Date and Time from Result:", updatedOn);

            // Extract and print date range
            var updatedOn = new Date(results[i].updated_on);
            var startDate = formatDate(updatedOn);
            var endDate = formatDate(new Date()); // Current date/time
            // var dateRange = endDate + ' - IST ';

            var dateRange = startDate + ' - ' + endDate;
            console.log("Date Range from Result:", dateRange);


        }
        var uniqueCount = Object.keys(uniqueDomains).length;

        // Update the count in the designated <div>
        $('.column[style="background-color:#aaaaaa50;"] h2').text(count);
        $('.column[style="background-color:#aaaaaa52;"] h2').text(uniqueCount);
        $('.column[style="background-color:#aaaaaa51;"] h2').text(dateRange);


        if (count === 0) {
            searchResultsDiv.append('<p>No Data found.</p>');
        } 
        // else {
        //     // Display each search result
        //     $.each(results, function(index, result) {
        //         searchResultsDiv.append('<h4><a href="' + result.url + '">' + result.url + '</a></h4>');
        //     });
        // }
    }

    function getDomain(url) {
        // Extract domain from the URL
        var domain;
        if (url.indexOf("://") > -1) {
            domain = url.split('/')[2];
        } else {
            domain = url.split('/')[0];
        }
        // Find and remove port number
        domain = domain.split(':')[0];
        return domain;
    }
    function formatDate(dateTimeString) {
        // Format date as "dd/mm/yyyy - dd/mm/yyyy"
        var dateTime = new Date(dateTimeString);
        var day = dateTime.getDate();
        var month = dateTime.getMonth() + 1;
        var year = dateTime.getFullYear();
        var hours = dateTime.getHours();
        var minutes = dateTime.getMinutes();
        var formattedDateTime = (day < 10 ? '0' : '') + day + '/' + (month < 10 ? '0' : '') + month + '/' + year + ' ' + (hours < 10 ? '0' : '') + hours + ':' + (minutes < 10 ? '0' : '') + minutes;
        return formattedDateTime;
    }
    function toggleSubURLs() {
        var subURLs = document.getElementById("subURLs");
        if (subURLs.style.display === "none") {
            subURLs.style.display = "block";
        } else {
            subURLs.style.display = "none";
        }
    }

    function toggleHomeURLs() {
        var homeURLS = document.getElementById("homeURLs");
        if (homeURLs.style.display === "none") {
            homeURLs.style.display = "block";
        } else {
            homeURLs.style.display = "none";
        }
    }

    function toggleUniqueURLs() {
        var uniqueURLs = document.getElementById("uniqueURLs");
        if (uniqueURLs.style.display === "none") {
            uniqueURLs.style.display = "block";
        } else {
            uniqueURLs.style.display = "none";
        }
    }


    function toggleSubURLs() {
        hideAllSectionsExcept('subURLs');
    }

    function toggleHomeURLs() {
        hideAllSectionsExcept('homeURLs');
    }

    function toggleAuthors() {
        hideAllSectionsExcept('authors');
    }

    function toggleUniqueURLs() {
        hideAllSectionsExcept('uniqueURLs')
    }

    function hideAllSectionsExcept(sectionId) {
        var sections = ['subURLs', 'homeURLs', 'authors', 'uniqueURLs'];
        sections.forEach(function(section) {
            if (section !== sectionId) {
                var sectionElement = document.getElementById(section);
                if (sectionElement.style.display === "block") {
                    sectionElement.style.display = "none";
                }
            }
        });
        var currentSection = document.getElementById(sectionId);
        currentSection.style.display = (currentSection.style.display === "block") ? "none" : "block";
    }

    function toggleAuthors() {
        var authorsDiv = document.getElementById("authors");
        var table = document.getElementById("authorTable");

        if (authorsDiv.style.display === "none") {
            authorsDiv.style.display = "block";
            table.style.display = "table"; // Show the table
        } else {
            authorsDiv.style.display = "none";
            table.style.display = "none"; // Hide the table
        }
    }

    function searchTable() {
        // Declare variables
        var input, filter, table, tr, td, i, txtValue;
        input = document.getElementById("searchInput");
        filter = input.value.toUpperCase();
        table = document.getElementById("authorTable");
        tr = table.getElementsByTagName("tr");

        // Loop through all table rows, and hide those that don't match the search query in Author or Category
        for (i = 0; i < tr.length; i++) {
            tdAuthor = tr[i].getElementsByTagName("td")[0]; // Search in the first column (Author)
            tdCategory = tr[i].getElementsByTagName("td")[3]; // Search in the fourth column (Category)
            if (tdAuthor && tdCategory) {
                txtValueAuthor = tdAuthor.textContent || tdAuthor.innerText;
                txtValueCategory = tdCategory.textContent || tdCategory.innerText;
                if (txtValueAuthor.toUpperCase().indexOf(filter) > -1 || txtValueCategory.toUpperCase().indexOf(filter) > -1) {
                    tr[i].style.display = "";
                } else {
                    tr[i].style.display = "none";
                }
            }
        }
    }



});