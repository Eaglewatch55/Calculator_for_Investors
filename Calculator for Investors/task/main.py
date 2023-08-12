import csv
from sqlalchemy import Column, Float, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import desc
from sqlalchemy.orm import sessionmaker, Query
from os import path


class Menu:
    def __init__(self, name, options: dict):
        self.menu_name = name
        self.menu_options = {i: opt for i, opt in enumerate(options.items())}

    def selection(self):

        print("Enter an option:")
        try:
            num = int(input())

        except ValueError:
            print("Invalid option!")
            print()
            return

        if num not in self.menu_options.keys():
            print("Invalid option!")
            print()
            return

        if not issubclass(self.__class__, SubMenu) and num != 0:
            print()

        return num

    def print_and_select(self):
        print(self.__str__())
        return self.selection()

    def exit_message(self, msg=None):
        pass

    def menu_selection(self):
        flag = True
        while flag:
            print(self.menu_name)
            selection = self.print_and_select()
            if selection is None:
                continue
            elif selection == 0:
                self.exit_message()
                break

            flag = self.menu_options[selection][1]()

        return True

    def __str__(self):
        to_return = []
        for i, row in self.menu_options.items():
            to_return.append(f"{i} {row[0]}")
        to_return = "\n".join(to_return) + "\n"
        return to_return


class MainMenu(Menu):
    def __init__(self, name, options: dict, submenus: dict):
        Menu.__init__(self, name, options)
        self.sub_menus = submenus

    def exit_message(self, msg="Have a nice day!"):
        print(msg)


class SubMenu(Menu):
    def __init__(self, name, companies):
        Menu.__init__(self, name, companies)


class CompaniesMenu(SubMenu):
    def __init__(self, companies: list):
        self.menu_options = {i: data for i, data in enumerate(companies)}

    def menu_selection(self):

        while True:

            selection = self.print_and_select()
            if selection is None:
                continue

            # print()
            break

        return self.menu_options[selection]

    def selection(self):
        print("Enter company number:")
        try:
            num = int(input())

        except ValueError:
            print("Invalid option!")
            print()
            return

        if num not in self.menu_options.keys():
            print("Invalid option!")
            print()
            return

        if not issubclass(self.__class__, SubMenu) and num != 0:
            print()

        return num


    def get_company(self, number):
        return self.menu_options[number]

    def __str__(self):
        to_return = []
        for i, row in self.menu_options.items():
            to_return.append(f"{i} {row.name}")
        to_return = "\n".join(to_return)
        return to_return


class TTMenu(SubMenu):
    def menu_selection(self):
        flag = True
        while flag:
            print(self.menu_name)
            selection = self.print_and_select()
            if selection is None:
                continue
            elif selection == 0 or selection is False:
                self.exit_message()
                break

            flag = self.menu_options[selection][1](selection)

        return True

    def selection(self):

        print("Enter an option:")
        try:
            num = int(input())

        except ValueError:
            print("Invalid option!")
            # print()
            return False

        if num not in self.menu_options.keys():
            print("Invalid option!")
            # print()
            return False

        if not issubclass(self.__class__, SubMenu) and num != 0:
            print()

        return num


Base = declarative_base()


class Companies(Base):
    __tablename__ = "companies"

    ticker = Column(String, primary_key=True)
    name = Column(String, server_default=None)
    sector = Column(String, server_default=None)


class Financial(Base):
    __tablename__ = "financial"

    ticker = Column(String, primary_key=True)
    ebitda = Column(Float, server_default=None)
    sales = Column(Float, server_default=None)
    net_profit = Column(Float, server_default=None)
    market_price = Column(Float, server_default=None)
    net_debt = Column(Float, server_default=None)
    assets = Column(Float, server_default=None)
    equity = Column(Float, server_default=None)
    cash_equivalents = Column(Float, server_default=None)
    liabilities = Column(Float, server_default=None)


engine = create_engine('sqlite:///investor.db', connect_args={'check_same_thread': False})

# Stage 2 - Create database an add data if db doesn't exist
# if created_companies and created_financial:
if not path.exists("investor.db"):
    def load_csv():
        def helper(f_name, table_type):
            to_return = []
            header = True

            with open(f_name, "r") as f:
                reader = csv.reader(f)

                for row in reader:
                    if header is True:
                        header = [i for i in row]
                        continue

                    if "" in row:
                        for j, data in enumerate(row):
                            if data == "":
                                row[j] = None

                    # Unpacks a dictionary created with the header and each row to create the object
                    to_return.append(table_type(**dict(zip(header, row))))

                return to_return

        company = helper("test/companies.csv", Companies)
        financial = helper("test/financial.csv", Financial)

        return company, financial

    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    for table in load_csv():
        for register in table:
            session.add(register)

    session.commit()
    # print("Database created successfully!")
    # exit()


def add_register_db(eng, data_dict: dict):
    Session = sessionmaker(bind=eng)
    session = Session()

    for t, d in data_dict.items():
        session.add(t(**d))

    session.commit()
    session.close()
    return


def update_register_db(eng, table, key_value, data: dict):
    Session = sessionmaker(bind=eng)
    session = Session()

    query = session.query(table)
    fil = query.filter(table.ticker == key_value)

    fil.update(data)

    session.commit()
    session.close()


def delete_register_db(eng, table, key_value):
    Session = sessionmaker(bind=eng)
    session = Session()

    query = session.query(table)
    query.filter(table.ticker == key_value).delete()

    session.commit()
    session.close()


def company_search(sess, company_name, t=Companies):
    query = sess.query(t)
    fil = query.filter(t.name.like(f"%{company_name}%")).all()
    query_list = list(fil)

    if len(query_list) == 0:
        return None
    else:
        return CompaniesMenu(query_list)


def create_fin_data(ticker):
    fin_data = {}

    if ticker is not False:
        fin_data["ticker"] = ticker

    print("Enter ebitda (in the format '987654321')")
    fin_data["ebitda"] = float(input())
    print("Enter sales (in the format '987654321'):")
    fin_data["sales"] = float(input())
    print("Enter net profit (in the format '987654321'):")
    fin_data["net_profit"] = float(input())
    print("Enter market price (in the format '987654321')")
    fin_data["market_price"] = float(input())
    print("Enter net debt (in the format '987654321'):")
    fin_data["net_debt"] = float(input())
    print("Enter assets (in the format '987654321'):")
    fin_data["assets"] = float(input())
    print("Enter equity (in the format '987654321'):")
    fin_data["equity"] = float(input())
    print("Enter cash equivalents (in the format '987654321'):")
    fin_data["cash_equivalents"] = float(input())
    print("Enter liabilities (in the format '987654321'):")
    fin_data["liabilities"] = float(input())
    return fin_data


def crud_create(eng=engine):
    comp_data = {}
    fin_data = {}

    print("Enter ticker (in the format 'MOON'):")
    comp_data["ticker"] = input()
    print("Enter company (in the format 'Moon Corp'):")
    comp_data["name"] = input()
    print("Enter industries (in the format 'Technology'):")
    comp_data["sector"] = input()

    fin_data = create_fin_data(comp_data["ticker"])

    table_dict = {Companies: comp_data, Financial: fin_data}

    add_register_db(eng, table_dict)
    print("Company created successfully!\n")


def crud_read(eng=engine):

    def metrics_calculation(num, denom):
        if denom is None:
            return None
        else:
            return round(num / denom, 2)

    print("Enter company name:")
    comp_name = input()

    Session = sessionmaker(bind=eng)
    session = Session()

    comp_menu = company_search(session, comp_name)

    if comp_menu is None:
        print("Company not found!\n")
        return

    sel_company = comp_menu.menu_selection()

    query = session.query(Financial)
    f_data = dict(query.filter(Financial.ticker == sel_company.ticker).first().__dict__)

    comp_data = dict()
    comp_data["P/E"] = metrics_calculation(f_data["market_price"], f_data["net_profit"])
    comp_data["P/S"] = metrics_calculation(f_data["market_price"], f_data["sales"])
    comp_data["P/B"] = metrics_calculation(f_data["market_price"], f_data["assets"])
    comp_data["ND/EBITDA"] = metrics_calculation(f_data["net_debt"], f_data["ebitda"])
    comp_data["ROE"] = metrics_calculation(f_data["net_profit"], f_data["equity"])
    comp_data["ROA"] = metrics_calculation(f_data["net_profit"], f_data["assets"])
    comp_data["L/A"] = metrics_calculation(f_data["liabilities"], f_data["assets"])

    print(sel_company.ticker, sel_company.name)

    for title, data in comp_data.items():
        print(title, "=", data)

    print()


def crud_update(eng=engine):
    print("Enter company name:")
    comp_name = input()

    Session = sessionmaker(bind=eng)
    session = Session()

    comp_menu = company_search(session, comp_name)

    if comp_menu is None:
        print("Company not found!")
        return

    sel_company = comp_menu.menu_selection()
    fin_data = create_fin_data(False)

    update_register_db(engine, Financial, sel_company.ticker, fin_data)
    print("Company updated successfully!\n")


def crud_delete(eng=engine):
    print("Enter company name:")
    comp_name = input()

    Session = sessionmaker(bind=eng)
    session = Session()

    comp_menu = company_search(session, comp_name)

    if comp_menu is None:
        print("Company not found!")
        return

    sel_company = comp_menu.menu_selection()

    for t in [Companies, Financial]:
        delete_register_db(engine, t, sel_company.ticker)

    print("Company deleted successfully!\n")


def crud_list_all(eng=engine):
    print("COMPANY LIST")

    Session = sessionmaker(bind=eng)
    session = Session()

    query = session.query(Companies).order_by(Companies.ticker)
    companies = query.all()

    for company in companies:
        print(company.ticker, company.name, company.sector)

    print()


def top_ten(metric, eng=engine):
    Session = sessionmaker(bind=eng)
    session = Session()

    match metric:
        case 1:
            operator = "ND/EBITDA"
            stmt = (Financial.ticker,
                    Financial.net_debt,
                    Financial.ebitda,
                    (Financial.net_debt / Financial.ebitda).label("operator"))
        case 2:
            operator = "ROE"
            stmt = (Financial.ticker,
                    Financial.net_profit,
                    Financial.equity,
                    (Financial.net_profit / Financial.equity).label("operator"))
        case 3:
            operator = "ROA"
            stmt = (Financial.ticker,
                    Financial.net_profit,
                    Financial.assets,
                    (Financial.net_profit / Financial.assets).label("operator"))

    query = session.query(*stmt).order_by(desc("operator")).limit(10)

    print(f"TICKER {operator}")

    for result in query:
        print(result.ticker, round(result.operator, 2))

    print()

    session.close()

print("Welcome to the Investor Program!\n")

crud_menu = SubMenu("CRUD MENU",
                    {"Back": None,
                     "Create a company": crud_create,
                     "Read a company": crud_read,
                     "Update a company": crud_update,
                     "Delete a company": crud_delete,
                     "List all companies": crud_list_all}
                    )

top_ten_menu = TTMenu("TOP TEN MENU",
                       {"Back": None,
                        "List by ND/EBITDA": top_ten,
                        "List by ROE": top_ten,
                        "List by ROA": top_ten}
                       )

main_menu = MainMenu("MAIN MENU",
                     {"Exit": None,
                      "CRUD operations": crud_menu.menu_selection,
                      "Show top ten companies by criteria": top_ten_menu.menu_selection},
                     {"TOP TEN MENU": top_ten_menu,
                      "CRUD MENU": crud_menu}
                     )

main_menu.menu_selection()
engine.dispose()

