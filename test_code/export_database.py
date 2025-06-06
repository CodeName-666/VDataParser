import argparse
import mysql.connector
import json
from dataclasses import asdict
from typing import List
from datetime import datetime


from objects.data_class_definition import *

def connect(args):
    """Testet die Verbindung zur MySQL-Datenbank."""
    try:
        conn = mysql.connector.connect(
            host=args.host,
            user=args.user,
            password=args.password,
            database=args.database
        )
        if conn.is_connected():
            print(f"Erfolgreich mit der Datenbank '{args.database}' auf {args.host} verbunden.")
        conn.close()
    except mysql.connector.Error as err:
        print(f"Fehler: {err}")


def export(args):
    """Exportiert die gesamte Datenbank in das gewünschte JSON-Format mit Dataclasses."""
    try:
        conn = mysql.connector.connect(
            host=args.host,
            user=args.user,
            password=args.password,
            database=args.database
        )
        cursor = conn.cursor(dictionary=True)

        # Header-Informationen
        header = HeaderDataClass(type="header", version="5.2.1", comment="Export to JSON plugin for Python")
        base_info = BaseInfoDataClass(type="database", name=args.database)

        main_numbers_list = []
        seller_data_list = None

        # Alle Tabellen abrufen
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()

        for table in tables:
            table_name = table[f"Tables_in_{args.database}"]
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()

            if table_name == "verkaeufer":  # Falls es sich um die Verkäufer-Tabelle handelt
                seller_data_list = SellerListDataClass(
                    type="table",
                    name=table_name,
                    database=args.database,
                    data=rows
                )
            else:  # Falls es sich um eine normale Artikeltabelle handelt
                main_numbers_list.append(MainNumberDataClass(
                    type="table",
                    name=table_name,
                    database=args.database,
                    data=rows
                ))

        if seller_data_list is None:
            seller_data_list = SellerListDataClass(
                type="table",
                name="verkaeufer",
                database=args.database,
                data=[]
            )

        # JSON-Datenstruktur mit Dataclasses erstellen
        json_data = JSONData(
            export_header=header,
            base_info=base_info,
            main_numbers_list=main_numbers_list,
            sellers=seller_data_list
        )

        # JSON in Datei speichern
        with open(args.output, 'w', encoding='utf-8') as json_file:
            json.dump(asdict(json_data), json_file, ensure_ascii=False, indent=4)

        print(f"Datenbank erfolgreich exportiert nach '{args.output}'.")

    except mysql.connector.Error as err:
        print(f"Fehler: {err}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


def main():
    parser = argparse.ArgumentParser(description="MySQL Datenbank Verbindung & Export in JSON")

    subparsers = parser.add_subparsers(title="Befehle", dest="command")
    subparsers.required = True

    # Subcommand: connect
    connect_parser = subparsers.add_parser("connect", help="Testet die Verbindung zur MySQL-Datenbank")
    connect_parser.add_argument("--host", required=True, help="Hostname oder IP der Datenbank")
    connect_parser.add_argument("--user", required=True, help="Datenbank-Benutzername")
    connect_parser.add_argument("--password", required=True, help="Datenbank-Passwort")
    connect_parser.add_argument("--database", required=True, help="Name der Datenbank")
    connect_parser.set_defaults(func=connect)

    #Subcommand: export
    export_parser = subparsers.add_parser("export", help="Exportiert die gesamte Datenbank als JSON-Datei")
    export_parser.add_argument("--host", required=True, help="Hostname oder IP der Datenbank")
    export_parser.add_argument("--user", required=True, help="Datenbank-Benutzername")
    export_parser.add_argument("--password", required=True, help="Datenbank-Passwort")
    export_parser.add_argument("--database", required=True, help="Name der Datenbank")
    export_parser.add_argument("--output", default="export.json", help="Name der JSON-Ausgabedatei (Standard: export.json)")
    export_parser.set_defaults(func=export)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
