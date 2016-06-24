# Qual TE Menu App  (QTEMenu) {#QTEReadme}

Qual TE Menu Application
========================

The MPS Qualification Software (Qual) is designed to be driven by external
software, referred to as the Test Equipment (TE) software.  In order to
provide for initial testing of the Qual Software while the final TE software
is being developed, a simple menu-driven test application called QTEMenu
has been developed.

When launched, QTEMenu displays a menu of Qual modules.  When a module is
chosen, a list of possible messages defined for that module is displayed.
Choosing a message causes QTEMenu to send that message to the Qual software
and wait for the response.

### Options

The Qual software supports both GPB and JSON-format messaging (see
[Qual Test App](@ref QTAReadme)).  QTEMenu uses GPB messaging by default;
to use JSON messaging instead, launch the application with the option `-j`.

QTEMenu will attempt to contact the Qual software running on the local host
by default; to connect to a remote server instead, launch the application
with the option `-s` _ipaddr_ where _ipaddr_ is the IP address of the
remote server.
