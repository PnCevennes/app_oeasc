export default {
  group: 'commons',
  name: 'content',
  label: 'Content',
  serverSide: true,

  defs: {
    id_content: {
      label: 'ID',
      type: 'text',
      hidden: true,
    },
    code: {
      label: 'Code',
      type: 'text',
      required: true,
    },
    md: {
      label: 'Markdown',
      type: 'text_area',
      required: true,
    },
    meta_create_date: {
      type: 'date',
      label: 'Création',
    },
    type_page: {
      type: 'text',
      label: 'Type',
    },
  },
};
