```

PLAY [nxos101] **********************************

TASK [Get the config using the filter] **********************************
unable to load netconf plugin for network_os cisco.nxos.nxos, falling back to default plugin
ok: [nxos101]

TASK [Random description] **********************************
ok: [nxos101]

TASK [Update] **********************************
changed: [nxos101]

TASK [Set the fact for the revised config] **********************************
ok: [nxos101]

TASK [Apply the new configuration] **********************************
changed: [nxos101]

TASK [Get the config using the filter] **********************************
ok: [nxos101]

TASK [Show the differences in a dot delimited format] **********************************
--- before
+++ after
@@ -9,7 +9,7 @@
     "data.System.intf-items.phys-items.PhysIf-list.bw": "0",
     "data.System.intf-items.phys-items.PhysIf-list.controllerId": null,
     "data.System.intf-items.phys-items.PhysIf-list.delay": "1",
-    "data.System.intf-items.phys-items.PhysIf-list.descr": "60",
+    "data.System.intf-items.phys-items.PhysIf-list.descr": "37",
     "data.System.intf-items.phys-items.PhysIf-list.dot1qEtherType": "0x8100",
     "data.System.intf-items.phys-items.PhysIf-list.duplex": "auto",
     "data.System.intf-items.phys-items.PhysIf-list.eeep-items.eeeLat": "variable",

changed: [nxos101]

TASK [Validate the configuration change] **********************************
ok: [nxos101]

PLAY RECAP **********************************
nxos101                    : ok=8    changed=3    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0   

(venv) ➜  xml_filters 
```