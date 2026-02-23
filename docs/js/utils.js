async function getJSON(url) {
  response = await fetch(url);
  if (response.status === 200) {
    return await response.json();
  } else {
    return {
      error: response.status,
    };
  }
}

// todo: filter releases by date or by first/last version number (before, since),
// e.g., for quantities, I only want to mention releases since I became maintainer (from 22/02/2019)
// while for Elephant, I only want to mention releases up to 0.5.0, when we last contributed

// todo: filter out pre-releases, removed releases, etc. (see ebrains-drive, for example)

function countReleases(releases) {
  return Object.keys(releases).length;
}

function getReleaseDates(releases) {
  const publicationDates = Object.values(releases).map((releaseArray) => {
    if (releaseArray.length > 0) {
      return releaseArray[0].upload_time;
    } else {
      return null;
    }
  });
  return publicationDates.filter((item) => item !== null);
}

function latestReleaseDate(releases) {
  return new Date(getReleaseDates(releases).reduce((a, b) => (a > b ? a : b)));
}

function firstReleaseDate(releases) {
  return new Date(getReleaseDates(releases).reduce((a, b) => (a < b ? a : b)));
}

function isValidRelease(version, releaseData) {
  if (version.includes("a")) {
    return false;
  } else if (version.includes("dev")) {
    return false;
  } else if (version.startsWith("0.0.")) {
    return false;
  } else {
    return true;
  }
}

function filterValidReleases(releases) {
  const validReleases = {};
  for (const version in releases) {
    if (isValidRelease(version, releases[version])) {
      validReleases[version] = releases[version];
    }
  }
  return validReleases;
}

async function renderProjects() {
  const activePythonProjects = [
    "PyNN",
    "neo",
    "sumatra",
    "fairgraph",
    "quantities",
    "lazyarray",
    "ebrains-drive",
    "openminds",
    "bids2openminds",
    "hippounit",
    "basalunit",
    "cerebunit",
    "morphounit",
    "ebrains-validation-framework",
    "hbp-neuromorphic-platform",
    "hbp-validation-framework",
  ];
  const inactivePythonProjects = [
    "elephant",
    "mozaik",
    "nineml",
    "NeuroTools",
    "parameters",
    "hbp-archive",
  ];
  const otherProjects = [
    "Neo Viewer",
    "Arkheia",
    "Helmholtz",
    "EBRAINS Neuromorphic Remote Access service",
    "EBRAINS Model Catalog",
    "EBRAINS Provenance API",
    "EBRAINS Workflow components library",
    "EBRAINS Live Papers service",
  ];

  const allPythonProjects = [
    ...activePythonProjects,
    ...inactivePythonProjects,
  ];
  // Note: older versions of PyNN (before 0.4.0) not on PyPI. First PyNN release 24 mai 2007 (0.1.0 or 0.2.0?)
  //       so need to over-ride info obtained from PyPI, adding 2 or 3 extra versions

  const projectData = {};
  const promises = allPythonProjects.map((projectName) =>
    getJSON(`https://pypi.org/pypi/${projectName}/json`)
  );
  const results = await Promise.all(promises);

  for (const result of results) {
    projectData[result.info.name] = result;
  }

  console.log(projectData);

  for (const projectName of Object.keys(projectData)) {
    console.log(projectData[projectName]);
    const releases = filterValidReleases(projectData[projectName].releases);
    const anchor = document.getElementById(projectName);
    console.log(projectName);
    if (anchor) {
      anchor.innerHTML += `<p>
        Most recent version: ${projectData[projectName].info.version}
        - released ${latestReleaseDate(releases).toDateString()}
      </p>`;
      anchor.innerHTML += `<p>${countReleases(
        releases
      )} versions published since ${firstReleaseDate(
        releases
      ).toDateString()}</p>`;
    }
  }

  document.querySelectorAll("td[id^='sw-version-']").forEach(cell => {
    const pkgName = cell.id.slice("sw-version-".length);
    const key = Object.keys(projectData).find(
      k => k.toLowerCase() === pkgName.toLowerCase()
    );
    if (key) {
      cell.textContent = projectData[key].info.version;
    }
  });
}
