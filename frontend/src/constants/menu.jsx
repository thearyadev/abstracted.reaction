import { adminRoot } from './defaultValues';

const data = [
  {
    id: 'dashboard',
    icon: 'iconsminds-home-1',
    label: 'dashboard',
    to: `${adminRoot}/dashboard`,
  },
  {
    id: 'films',
    icon: 'simple-icon-film',
    label: 'films',
    to: `${adminRoot}/films`,
  },
  {
    id: 'actresses',
    icon: 'simple-icon-symbol-female',
    label: 'actresses',
    to: `${adminRoot}/actresses`,
  },
  {
    id: "import",
    icon: "simple-icon-cloud-download",
    label: 'import',
    to: `${adminRoot}/import`
  }
];
export default data;
