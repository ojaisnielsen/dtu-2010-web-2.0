function getReferences(entityDesc) {
    entityDetails = entityDesc.split("/");
    if (entityDetails.length == 1) {
        return document.getElementsByClassName(entityDesc);
    }
    if (entityDetails.length == 2) {
        var references = new Array();
        entityTypeInstances = document.getElementsByClassName(entityDetails[0]);
        for (i = 0; i < entityTypeInstances.length; i++) {
            if (entityTypeInstances[i].attributes["title"].value == entityDetails[1]) {
                references[i] = entityTypeInstances[i];
            }
        }
        return references;
    }
}

function displayInfo(id) {
    node = document.getElementById(id);
    siblings = node.parentNode.childNodes;
    for (i = 0; i < siblings.length; i++) {
        siblings[i].style.display = "none";
    }
    node.style.display = "inline";
}

function deselectEntities(entityDesc) {
    entityReferences = getReferences(entityDesc);
    for (i = 0; i < entityReferences.length; i++) {
        entityReferences[i].className = entityReferences[i].className.replace("SELECTED", "");
    }
}

function selectEntity(entityDesc) {
    entityType = entityDesc.split("/")[0];
    entityName = entityDesc.split("/")[1];
    deselectEntities(entityType);
    entityReferences = getReferences(entityDesc);
    for (i in entityReferences) {
        entityReferences[i].className += " SELECTED";
    }
    document.getElementById("entities").elements[entityType].value = entityName;
}

function updateSubmitter() {
    currentUrl = document.getElementById("submit").attributes["href"].value;
    urlParts = currentUrl.split("?");
    url = "";
    if (urlParts.length == 0) {
        url = currentUrl
    }
    else {
        url = urlParts[0]
    }
    url += "?";
    entityInputs = document.getElementById("entities").getElementsByTagName("input");
    for (i = 0; i < entityInputs.length; i++) {
        entityType = entityInputs[i].attributes["name"].value
        entityName = document.getElementById("entities").elements[entityType].value
        url += entityType + "=" + entityName + "&";
    }
    document.getElementById("submit").attributes["href"].value = url;
}

