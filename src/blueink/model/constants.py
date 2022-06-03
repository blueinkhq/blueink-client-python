ATTACHMENT_TYPE = Munch(
    JPG="jpg",
    JPEG="jpeg",
    PNG="png",
    GIF="gif",
    SVG="svg",
    PDF="pdf",
    DOC="doc",
    DOCX="docx",
    PPT="ppt",
    PPTX="pptx",
    XLS="xls",
    XLSX="xlsx",
    RTF="rtf",
    TXT="txt",
)

BUNDLE_ORDER = Munch(
    CREATED="created",
    SENT="sent",
    COMPLETED_AT="completed_at",
)

BUNDLE_STATUS = Munch(
    NEW="ne",
    DRAFT="dr",
    PENDING="pe",
    SENT="se",
    STARTED="st",
    CANCELLED="ca",
    EXPIRED="ex",
    COMPLETE="co",
    FAILED="fa",
)

DELIVER_VIA = Munch(
    EMAIL="em",
    SMS="sm",
    KIOSK="ki",
    BOTH="bo",
)

FIELD_KIND = Munch(
    ESIGNATURE="sig",
    INITIALS="ini",
    SIGNERNAME="snm",
    SIGNINGDATE="sdt",
    INPUT="inp",
    TEXT="txt",
    DATE="dat",
    CHECKBOX="chk",
    CHECKBOXES="cbx",
    ATTACHMENT="att",
)

PACKET_STATUS = Munch(
    NEW="ne",
    READY="re",
    SENT="se",
    STARTED="st",
    CANCELLED="ca",
    EXPIRED="ex",
    COMPLETE="co",
    FAILED="fa",
)

V_PATTERN = Munch(
    EMAIL="email",
    BANK_ROUTING="bank_routing",
    BANK_ACCOUNT="bank_account",
    LETTERS="letters",
    NUMBERS="numbers",
    PHONE="phone",
    SSN="ssn",
    ZIP_CODE="zip_code",
)