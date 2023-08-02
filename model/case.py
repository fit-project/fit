#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######
from pathlib import Path

from model.db import Db

import os

from sqlalchemy import ForeignKey, Column, Integer, String, Text, LargeBinary
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Case(Base):
    __tablename__ = "cases"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    lawyer_name = Column(String)
    operator = Column(String)
    proceeding_type = Column(Integer)
    courthouse = Column(String)
    proceeding_number = Column(Integer)
    notes = Column(Text)
    logo_bin = Column(LargeBinary)
    logo = Column(String)
    logo_height = Column(String)
    logo_width = Column(String)

    def __init__(self) -> None:
        super().__init__()
        self.db = Db()
        self.metadata.create_all(self.db.engine)

    def get(self):
        return self.db.session.query(Case).all()

    def get_from_id(self, id):
        return self.db.session.query(Case).filter_by(id=id).one()

    def update(self, case_info):
        if os.path.isfile(case_info["logo"]):
            case_info["logo_bin"] = self.__set_logo_bin(case_info["logo"])

        self.db.session.query(Case).filter(Case.id == case_info.get("id")).update(
            case_info
        )
        self.db.session.commit()

    def add(self, case_info):
        case = Case()
        case.name = case_info["name"]
        case.lawyer_name = case_info["lawyer_name"]
        case.operator = case_info["operator"]
        case.proceeding_type = case_info["proceeding_type"]
        case.courthouse = case_info["courthouse"]
        case.proceeding_number = case_info["proceeding_number"]
        case.notes = case_info["notes"]
        case.logo = case_info["logo"]
        case.logo_height = case_info["logo_height"]
        case.logo_width = case_info["logo_width"]
        if os.path.isfile(case.logo):
            case.logo_bin = self.__set_logo_bin(case.logo)

        self.db.session.add(case)
        self.db.session.commit()

        return self.db.session.query(Case).order_by(Case.id.desc()).first()

    def __set_logo_bin(self, file_path):
        with open(file_path, "rb") as file:
            return file.read()

    def create_acquisition_directory(self, directories):
        acquisition_type_directory = os.path.join(
            os.path.expanduser(directories["cases_folder"]),
            directories["case_folder"],
            directories["acquisition_type_folder"],
        )

        acquisition_directory = os.path.join(
            acquisition_type_directory, "acquisition_1"
        )

        if os.path.isdir(acquisition_directory):
            # Get all subdirectories from acquisition directory
            acquisition_directories = [
                d
                for d in os.listdir(acquisition_type_directory)
                if os.path.isdir(os.path.join(acquisition_type_directory, d))
            ]

            # select the highest number in sufix name
            index = max(
                [
                    int("".join(filter(str.isdigit, item)))
                    for item in acquisition_directories
                ]
            )

            # Increment index and create the new content folder
            acquisition_directory = os.path.join(
                acquisition_type_directory, "acquisition_" + str(index + 1)
            )

        os.makedirs(acquisition_directory)

        return acquisition_directory

    def get_case_directory_list(self, cases_folder):
        subfolders = [f.name for f in os.scandir(cases_folder) if f.is_dir()]

        return subfolders
