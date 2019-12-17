import os

from rest_framework import (
    reverse,
    status,
    test,
)


class ProcedureSiteTest(test.APITestCase):
    fixtures = [
        os.path.join('fixtures', 'test_editors.json')
    ]

    def test_create_site(self):
        url_create = reverse.reverse('editors:sites-list')
        response = self.client.post(
            url_create,
            data={'signature': 'basic'}
        )
        self.assertEqual(
            response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data.get('signature'), 'basic')

    def test_destroy_site(self):
        url_destroy = reverse.reverse('editors:sites-detail', ['test-site-1'])
        response = self.client.delete(url_destroy)
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

        url_destroy = reverse.reverse('editors:sites-detail', ['test-site-2'])
        response = self.client.delete(url_destroy)
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

        url_destroy = reverse.reverse('editors:sites-detail', ['test-site-3'])
        response = self.client.delete(url_destroy)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_list_site(self):
        url_list = reverse.reverse('editors:sites-list')
        response = self.client.get(url_list)
        self.assertEqual(
            response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count'), 3)

    def test_create_sub_sites(self):
        url_base_sites = reverse.reverse(
            'editors:site-base-sites-list', ['test-site-3'])
        response = self.client.post(
            url_base_sites, data={'signature': 'test-site-1'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data.get('signature'), 'test-site-1')

        response = self.client.post(
            url_base_sites, data={'signature': 'test-site-1'})
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    def test_list_sub_sites(self):
        url_base_sites = reverse.reverse(
            'editors:site-base-sites-list', ['test-site-3'])
        response = self.client.get(url_base_sites)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count'), 1)

    def test_destroy_sub_sites(self):
        url_base_sites = reverse.reverse(
            'editors:site-base-sites-detail', ['test-site-3', 'test-site-2'])
        response = self.client.delete(url_base_sites)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        url_base_sites = reverse.reverse(
            'editors:site-base-sites-detail', ['test-site-3', 'test-site-1'])
        response = self.client.delete(url_base_sites)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class ProcedureTest(test.APITestCase):

    def test_create_procedure(self):
        pass

    def test_destroy_procedure(self):
        pass

    def test_list_procedure(self):
        pass

    def test_update_procedure(self):
        pass

    def test_retrieve_procedure(self):
        pass


class ProcedureJointTest(test.APITestCase):

    def test_create_joint(self):
        pass

    def test_destroy_joint(self):
        pass

    def test_list_joint(self):
        pass

    def test_update_joint(self):
        pass

    def test_retrieve_joint(self):
        pass


class ProcedureOutputTest(test.APITestCase):

    def test_create_output(self):
        pass

    def test_destroy_output(self):
        pass

    def test_list_output(self):
        pass

    def test_update_output(self):
        pass

    def test_retrieve_output(self):
        pass
