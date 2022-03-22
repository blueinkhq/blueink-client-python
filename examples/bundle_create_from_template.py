import sys

from blueinkclient import Client
from model.bundles import BundleBuilder


def print_no_templates_message_and_exit():
    print('No Document Templates found.')
    print(
        '\nTo create a Bundle using a Document Template, '
        'please add at least 1 Document Template to your account first.'
    )
    print('\nExiting now...')
    sys.exit()


if __name__ == "__main__":
    client = Client()

    templates = client.templates.list()
    if not templates.data:
        print_no_templates_message_and_exit()

    print('Retrieved {} Document Templates (of {} total results)\n{}\n'.format(
        len(templates.data),
        templates.pagination.total_results,
        '=' * 60
    ))

    for idx, tpl in enumerate(templates.data, start=1):
        print('{:2}: {} -- [{} Signer Roles, {} Fields]'.format(
            idx, tpl.name or tpl.id, len(tpl.roles), len(tpl.fields)
        ))

    selected_tpl = None
    while not selected_tpl:
        try:
            selected_tpl_raw = input('Please select a template [1 to {}]: '.format(len(templates.data)))
            selected_tpl_idx = int(selected_tpl_raw)
            selected_tpl = templates.data[selected_tpl_idx - 1]
        except (ValueError, IndexError):
            print('Please try again and enter a valid integer index')

    # Create a test Bundle, using a BundleBuilder helper class

    # FIXME - none of the BundleBuilder fields should be required
    builder = BundleBuilder(label='Test API Bundle with a Document Template',
                            email_subj='The Test Bundle you Created',
                            is_test=True)

    # FIXME - we need to be able to add Document Templates or new documents. Not sure
    #  if this should be a separate method or not, but the data schema for a template is different
    builder.add_document_template(selected_tpl.id)

    print('This template has {} signer role(s)'.format(len(selected_tpl.data.roles)))
    for role in enumerate(selected_tpl.roles, start=1):
        name = input('Please enter the name for Signer {}: '.format(idx))
        email = input('Please enter an email for Signer {}: '.format(idx))

        builder.add_signer(name, email)

        # FIXME - how to associate a signer with a document template role?
        #  With the chainable builder interface, it is not clear how to reference
        #  a previously added document (or signer, if we added signers first).
        #  With start_document() we know what document we are working on, but then we need a way
        #  to reference the signer. We could lookup the signer by email / phone (instead of signer key),
        #  but email / phone is not guaranteed to be unique. (e.g a signer could fill multiple roles)
        builder.assign_signer(email, role)


