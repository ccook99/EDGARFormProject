from bs4 import BeautifulSoup
import requests


def convert_tag_to_string(tag):
    return tag.text if tag is not None else ""


class FileParser:

    def __init__(self, url, accession_number):
        self.an = accession_number
        self.doc = self.get_ownership_doc_from_url(url)
        self.data = self.fill_data()


    def get_ownership_doc_from_url(self, url):
        page = requests.get(url)
        page.close()
        soup = BeautifulSoup(page.content, "xml")
        ownershipdoc = soup.find("ownershipDocument")

        return ownershipdoc

    def get_doc(self):
        return self.doc

    def get_data(self):
        return self.data

    # collect all listed owners
    def get_owners(self):
        return self.doc.findAll("reportingOwner")

    def fill_data(self):
        owners = []
        transactions = []

        for owner in self.get_owners():
            o = {"ownername": convert_tag_to_string(self.get_ownername(owner)),
                 "ownercik": convert_tag_to_string(self.get_ownercik(owner)),
                 "officertitle": convert_tag_to_string(self.get_officertitle(owner)),
                 "isdirector": convert_tag_to_string(self.get_isdirector(owner)),
                 "isofficer": convert_tag_to_string(self.get_isofficer(owner)),
                 "istenpercentowner": convert_tag_to_string(self.get_istenpercentowner(owner))}

            owners.append(o)

        counter = 0

        for transaction in self.get_ndts():
            t = {"accessionnumber": self.an,
                 "issuername": convert_tag_to_string(self.get_issuername()),
                 "issuercik": convert_tag_to_string(self.get_issuercik()),
                 "ticker": convert_tag_to_string(self.get_ticker()),
                 "filingdate": convert_tag_to_string(self.get_filingdate()),
                 "formtype": convert_tag_to_string(self.get_formtype()),
                 "securitytitle": convert_tag_to_string(self.get_securitytitle(transaction)),
                 "transactiondate": convert_tag_to_string(self.get_transactiondate(transaction)),
                 "transactioncode": convert_tag_to_string(self.get_transactioncode(transaction)),
                 "equityswapinvolved": convert_tag_to_string(self.get_equityswapinvolved(transaction)),
                 "transactionshares": convert_tag_to_string(self.get_transactionshares(transaction)),
                 "transactionpricepershare": convert_tag_to_string(self.get_transactionpricepershare(transaction)),
                 "transactionacquireddisposedcode": convert_tag_to_string(
                     self.get_transactionacquireddisposedcode(transaction)),
                 "sharesfollowingtransaction": convert_tag_to_string(
                     self.get_sharesownedfollowingtransaction(transaction)),
                 "ownershipdirectindirect": convert_tag_to_string(self.get_ownershipdirectindirect(transaction)),
                 "transactionnumber": counter}
            counter += 1

            transactions.append(t)

        d = {"owners": owners,
             "transactions": transactions}

        return d

    # returns the ticker of shares in transaction
    def get_ticker(self):
        return self.doc.find("issuerTradingSymbol")

    # returns the filing date of the form
    def get_filingdate(self):
        return self.doc.find("periodOfReport")

    # returns the form type
    def get_formtype(self):
        return self.doc.find("documentType")

    # returns the issuer's full (submitted) name
    def get_issuername(self):
        return self.doc.find("issuerName")

    # returns the cik of the issuer
    def get_issuercik(self):
        return self.doc.find("issuerCik")

    # GIVEN AN OWNER ("reportingOwner") ------------------------

    # returns the full (submitted) name of the owner
    def get_ownername(self, owner):
        return owner.find("rptOwnerName")

    # returns the cik of the owner
    def get_ownercik(self, owner):
        return owner.find("rptOwnerCik")

    # returns the full (submitted) officer title
    def get_officertitle(self, owner):
        return owner.find("officerTitle")

    # returns whether the owner is a director
    def get_isdirector(self, owner):
        return owner.find("isDirector")

    # returns whether the owner is an officer
    def get_isofficer(self, owner):
        return owner.find("isOfficer")

    # returns whether the owner is a 10% owner
    def get_istenpercentowner(self, owner):
        return owner.find("isTenPercentOwner")

    # ------------------------------------------------------------

    # GIVEN A TRANSACTION ("nonDerivativeTransaction") -----------

    # returns the transaction date for the given transaction
    def get_transactiondate(self, transaction):
        return transaction.find("transactionDate").find("value")

    # returns the transaction code of the given transaction (https://www.sec.gov/files/form4data%2C0.pdf)
    def get_transactioncode(self, transaction):
        return transaction.find("transactionCode")

    # returns the number of shares part of the transaction
    def get_transactionshares(self, transaction):
        return transaction.find("transactionShares").find("value")

    # returns the price per share for the transaction
    def get_transactionpricepershare(self, transaction):
        return transaction.find("transactionPricePerShare").find("value")

    # returns whether the shares were acquired or disposed
    def get_transactionacquireddisposedcode(self, transaction):
        return transaction.find("transactionAcquiredDisposedCode").find("value")

    # returns the number of shares owned following the transaction
    def get_sharesownedfollowingtransaction(self, transaction):
        return transaction.find("sharesOwnedFollowingTransaction").find("value")

    # returns whether the ownership is direct or indirect
    def get_ownershipdirectindirect(self, transaction):
        return transaction.find("directOrIndirectOwnership").find("value")

    # returns the title of the security
    def get_securitytitle(self, transaction):
        return transaction.find("securityTitle").find("value")

    # returns whether an equity swap was involved
    def get_equityswapinvolved(self, transaction):
        return transaction.find("equitySwapInvolved")

    # --------------------------------------------------------------

    # returns all of the non-derivative transactions
    def get_ndts(self):
        return self.doc.findAll("nonDerivativeTransaction")

    # returns the number of non-derivative transactions
    def get_ndt_length(self):
        return len(self.get_ndts())


#print(FileParser("https://www.sec.gov/Archives/edgar/data/1182464/000120919120025998/0001209191-20-025998.txt").get_data())
