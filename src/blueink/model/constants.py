class FieldKinds:
    ESIGNATURE = 'sig'
    INITIALS = 'ini'
    SIGNERNAME = 'snm'
    SIGNINGDATE = 'sdt'
    INPUT = 'inp'
    TEXT = 'txt'
    DATE = 'dat'
    CHECKBOX = 'chk'
    CHECKBOXES = 'cbx'
    ATTACHMENT = 'att'


class BundleStatuses:
    NEW = 'ne'
    DRAFT = 'dr'
    PENDING = 'pe'
    SENT = 'se'
    STARTED = 'st'
    CANCELLED = 'ca'
    EXPIRED = 'ex'
    COMPLETE = 'co'
    FAILED = 'fa'


class PacketDeliverVias:
    EMAIL = 'em'
    SMS = 'sm'
    KIOSK = 'ki'
    BOTH = 'bo'

