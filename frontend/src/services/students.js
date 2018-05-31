import * as R from 'ramda';

// TODO should find a better value than 0 here?
export const ALL_STUDENTS_SECTION = {value: 0, name: 'All Students'};

export const sortableNameToFirstName = sn => R.trim(R.last(R.split(', ', sn)));

export const makeStudentEntry = student => ({
  id: student.id,
  name: student.sortableName,
  sections: student.sections
});

export const alphabeticalComparator = (a, b) => {
  if(a.name.toLowerCase() < b.name.toLowerCase()) {
    return -1;
  }
  if(a.name.toLowerCase() > b.name.toLowerCase()) {
    return 1;
  }
  return 0;
};

const namesFromSections = ss => ss.map(s => s.name);

export const allSectionsForDisplay = R.pipe(
  namesFromSections,
  R.intersperse(', '),
  R.reduce(R.concat, '')
);

const combineEntrySections = (acc, next) => {
  const sections = next.sections;

  for(let i = 0; i < sections.length; i++) {
    if(!acc.hasOwnProperty(sections[i].id)) {
      acc[sections[i]['id']] = sections[i].name;
    }
  }

  return acc;
};

const entriesToSectionsById = R.reduce(combineEntrySections, {});

export const entriesToFilterChoices = entries => {
  const sectionsById = entriesToSectionsById(entries);
  sectionsById[ALL_STUDENTS_SECTION.value] = 'All Students';
  return Object.entries(sectionsById)
    .map(([id, name]) => ({value: parseInt(id), name: name}))
    .sort((a, b) => a.value - b.value);
};

export const rowMatchesStudentNameFilter = (value, entry) => {
  return value === '' || entry.name.toLowerCase().includes(value.toLowerCase());
};

export const rowMatchesSectionFilter = (value, entry) => {
  const selectedSectionId = value.value;
  if(selectedSectionId === ALL_STUDENTS_SECTION.value) {
    return true;
  }
  else {
    const sectionIds = entry.sections.map(s => s.id);
    return sectionIds.includes(selectedSectionId);
  }
};
