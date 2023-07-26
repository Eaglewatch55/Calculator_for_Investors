import csv
from sqlalchemy import Column, Float, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

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
                print()
                break

            print()
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
    pass


def not_implemented():
    print("Not implemented!")
    print()
    return False


engine = create_engine('sqlite:///investor.db')
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


def read_csv():
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
                    for i, data in enumerate(row):
                        if data == "":
                            row[i] = None

                # Unpacks a dictionary created with the header and each row to create the object
                to_return.append(table_type(**dict(zip(header, row))))

            return to_return

    company = helper("test/companies.csv", Companies)
    financial = helper("test/financial.csv", Financial)

    return company, financial


Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

for table in read_csv():
    for register in table:
        session.add(register)

session.commit()
engine.dispose()

print("Database created successfully!")

exit()
crud_menu = SubMenu("CRUD MENU",
                    {"Back": None,
                     "Create a company": not_implemented,
                     "Read a company": not_implemented,
                     "Update a company": not_implemented,
                     "Delete a company": not_implemented,
                     "List all companies": not_implemented}
                    )

top_ten_menu = SubMenu("TOP TEN MENU",
                       {"Back": None,
                        "List by ND/EBITDA": not_implemented,
                        "List by ROE": not_implemented,
                        "List by ROA": not_implemented}
                       )

main_menu = MainMenu("MAIN MENU",
                     {"Exit": None,
                      "CRUD operations": crud_menu.menu_selection,
                      "Show top ten companies by criteria": top_ten_menu.menu_selection},
                     {"TOP TEN MENU": top_ten_menu,
                      "CRUD MENU": crud_menu}
                     )

main_menu.menu_selection()



