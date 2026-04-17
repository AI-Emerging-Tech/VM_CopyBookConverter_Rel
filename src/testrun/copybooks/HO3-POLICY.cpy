       01 HO3-POLICY-RECORD.

           05 POLICY-HEADER.
              10 POLICY-NUMBER        PIC X(10).
              10 INSURED-NAME         PIC X(30).
              10 EFFECTIVE-DATE       PIC 9(8).
              10 EXPIRY-DATE          PIC 9(8).
              10 STATE-CODE           PIC X(2).

           05 POLICY-COVERAGES.
              10 COV-A-DWELLING       PIC 9(7)V99 COMP-3.
              10 COV-C-CONTENTS       PIC 9(7)V99 COMP-3.
              10 COV-E-LIABILITY      PIC 9(7)V99 COMP-3.
              10 ALL-PERIL-DEDUCTIBLE PIC 9(5)V99 COMP-3.

           05 MORTGAGEE-INFO.
              10 MORTGAGEE-NAME       PIC X(30).

           05 PROPERTY-COUNT          PIC S9(4) COMP.

           05 PROPERTY-DETAILS OCCURS 3 TIMES.
              10 PROPERTY-SEQ-NO      PIC X(2).
              10 YEAR-BUILT           PIC 9(4).
              10 OCCUPANCY-TYPE       PIC X(1).
              10 ROOF-TYPE            PIC X(1).
              10 PROPERTY-ADDRESS     PIC X(50).
              10 PROPERTY-CITY        PIC X(30).
              10 PROPERTY-ZIP         PIC X(5).
              10 PROPERTY-INSURED-VALUE PIC 9(7)V99 COMP-3.