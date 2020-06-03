from app import create_app
import unittest
import os

app = create_app()

class FlaskTestCase(unittest.TestCase):
    
    def setUp(self):
        # print("\nSet Up")
        self.tester = app.test_client(self)
        
    def tearDown(self):
        # print("Tear Down")
        pass

    def login(self):
        return self.tester.post("/login", data=dict(email=os.environ["TEST_USERNAME"],password=os.environ["TEST_PASSWORD"]), follow_redirects=True)
        
    # Ensure that flask was set up correctly
    def test_index(self):
        print("Test Get Index")
        response = self.tester.get("/home", content_type="html/text")
        self.assertEqual(response.status_code, 200)

    # Test Login Page Load
    def test_login_page_load(self):
        print("Test Get Login")
        response = self.tester.get("/login", content_type="html/text")
        self.assertTrue(b"Log In" in response.data)

    #Ensure login behaves correctly
    def test_correct_login(self):
        print("Test Post Login")
        response = self.login()
        self.assertIn(b"Welcome", response.data)

    #Ensure creating new post behaves correctly
    def test_create_post(self):
        print("Test Create Post")
        self.login()
        response=self.tester.get("/account", follow_redirects=True)
        self.assertIn(b"Account Info", response.data)
        
    #Ensure logging out behaves correctly
    def test_logout(self):
        print("Test Log Out")
        self.login()
        response=self.tester.get("/logout", follow_redirects=True)
        self.assertIn(b"Log In", response.data)


if __name__ == "__main__":
    unittest.main()
