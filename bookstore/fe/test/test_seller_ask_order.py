import pytest
import json
from fe.access.buyer import Buyer
from fe.test.gen_book_data import GenBook
from fe.access.new_buyer import register_new_buyer
from fe.access.book import Book
from fe.access.seller import Seller
from fe.access.new_seller import register_new_seller  
import uuid


class TestPayment:
    seller_id: str
    store_id: str
    buyer_id: str
    password: str
    buy_book_info_list: [Book]
    total_price: int
    order_id: str
    buyer: Buyer
    seller: Seller

    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.seller_id = "test_payment_seller_id_{}".format(str(uuid.uuid1()))
        self.store_id = "test_payment_store_id_{}".format(str(uuid.uuid1()))
        self.buyer_id = "test_payment_buyer_id_{}".format(str(uuid.uuid1()))
        self.password = self.seller_id
        gen_book = GenBook(self.seller_id, self.store_id)
        ok, buy_book_id_list = gen_book.gen(
            non_exist_book_id=False, low_stock_level=False, max_book_count=5
        )
        self.buy_book_info_list = gen_book.buy_book_info_list
        assert ok
        b = register_new_buyer(self.buyer_id, self.password)
        self.seller = register_new_seller(self.seller_id, self.password)
        self.buyer = b
        code, self.order_id = b.new_order(self.store_id, buy_book_id_list)
        assert code == 200
        self.total_price = 0
        for item in self.buy_book_info_list:
            book: Book = item[0]
            num = item[1]
            if book.price is None:
                continue
            else:
                self.total_price = self.total_price + book.price * num
        yield

    def test_ok(self):
        code = self.buyer.add_funds(self.total_price)
        assert code == 200
        code = self.buyer.payment(self.order_id)
        assert code == 200
        res= self.seller.get_order_list(user_id=self.buyer_id,store_id=self.store_id,status=None,order_id=None)
        print(res)
        assert res[0] == 200
        jsonn=res[1]
        for item in jsonn['order_list']:
            assert item['order_id']==self.order_id
            assert item['status']=='paid_unsent' 
        code=self.seller.sent_order(self.seller_id, self.store_id, self.order_id)
        assert code == 200
        res= self.seller.get_order_list(user_id=self.buyer_id,store_id=self.store_id,status=None,order_id=None)
        assert res[0] == 200
        print(res)
        jsonn=res[1]
        for item in jsonn['order_list']:
            assert item['order_id']==self.order_id
            assert item['status']=='sent_unreceived'
        code=self.buyer.receive_order(self.store_id,self.order_id)
        assert code == 200
        res= self.seller.get_order_list(user_id=self.buyer_id,store_id=self.store_id,status=None,order_id=None)
        assert res[0] == 200
        print(res)
        jsonn=res[1]
        for item in jsonn['order_list']:
            assert item['order_id']==self.order_id
            assert item['status']=='received'
        

        
    