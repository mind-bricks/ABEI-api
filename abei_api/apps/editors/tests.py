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
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count'), 3)

        url_list = reverse.reverse('editors:sites-list')
        response = self.client.get(
            url_list, QUERY_STRING='signature=test-site-1')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count'), 1)

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
    fixtures = [
        os.path.join('fixtures', 'test_editors.json')
    ]

    def test_create_procedure(self):
        url_list = reverse.reverse('editors:procedures-list')
        response = self.client.post(url_list, data={
            'signature': 'test-procedure',
            'docstring': 'test-procedure-doc',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(url_list, data={
            'signature': 'test-procedure',
            'site': 'test-site-1',
            'docstring': 'test-procedure-doc',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('joints', response.data)
        self.assertIn('inputs', response.data)
        self.assertIn('outputs', response.data)
        self.assertEqual(response.data.get('signature'), 'test-procedure')
        self.assertEqual(response.data.get('docstring'), 'test-procedure-doc')

    def test_destroy_procedure(self):
        url_detail_1 = reverse.reverse(
            'editors:procedures-detail', ['test-procedure-1'])
        response = self.client.delete(url_detail_1)
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

        url_detail_2 = reverse.reverse(
            'editors:procedures-detail', ['test-procedure-2'])
        response = self.client.delete(url_detail_2)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_list_procedure(self):
        url_list = reverse.reverse('editors:procedures-list')
        response = self.client.get(url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count'), 3)

        response = self.client.get(
            url_list, QUERY_STRING='signature=test-procedure-1')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count'), 1)

        response = self.client.get(
            url_list, QUERY_STRING='site=test-site-1')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count'), 2)

    def test_update_procedure(self):
        url_detail = reverse.reverse(
            'editors:procedures-detail', ['test-procedure-1'])
        response = self.client.patch(url_detail, data={
            'signature': 'test-procedure-1-1',
            'docstring': 'test-procedure-doc-1-1',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data.get('signature'), 'test-procedure-1-1')
        self.assertEqual(
            response.data.get('docstring'), 'test-procedure-doc-1-1')

    def test_retrieve_procedure(self):
        url_detail = reverse.reverse(
            'editors:procedures-detail', ['test-procedure-1'])
        response = self.client.get(url_detail)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_procedure_input(self):
        url_input_list = reverse.reverse(
            'editors:procedure-inputs-list', ['test-procedure-1'])
        response = self.client.post(url_input_list, data={
            'signature': 'test-input-1',
            'index': 1,
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('index', response.data)

        response = self.client.post(url_input_list, data={
            'signature': 'test-input-1',
            'index': 0,
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_destroy_procedure_input(self):
        url_input_detail = reverse.reverse(
            'editors:procedure-inputs-detail', ['test-procedure-1', 0])
        response = self.client.delete(url_input_detail)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.delete(url_input_detail)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_procedure_input(self):
        url_input_list = reverse.reverse(
            'editors:procedure-inputs-list', ['test-procedure-1'])
        response = self.client.get(url_input_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count'), 1)

    def test_update_procedure_input(self):
        url_input_detail = reverse.reverse(
            'editors:procedure-inputs-detail', ['test-procedure-1', 0])
        response = self.client.patch(url_input_detail, data={
            'index': 10,
            'signature': 'test-input-10',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('index'), 10)

        response = self.client.get(url_input_detail)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        url_input_detail = reverse.reverse(
            'editors:procedure-inputs-detail', ['test-procedure-1', 10])
        response = self.client.get(url_input_detail)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('index'), 10)


class ProcedureJointTest(test.APITestCase):
    fixtures = [
        os.path.join('fixtures', 'test_editors.json')
    ]

    def test_create_joint(self):
        url_list = reverse.reverse(
            'editors:procedure-joints-list', ['test-procedure-2'])
        response = self.client.post(url_list, data={
            'signature': 'test-joint-1',
            'procedure': 'test-procedure-1',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post(url_list, data={
            'signature': 'test-joint-2',
            'procedure': 'test-procedure-2',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_destroy_joint(self):
        url_detail = reverse.reverse('editors:procedure-joints-detail', [
            'test-procedure-2',
            'test-procedure-2-joint-1',
        ])
        response = self.client.delete(url_detail)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_list_joint(self):
        url_list = reverse.reverse(
            'editors:procedure-joints-list', ['test-procedure-2'])
        response = self.client.get(url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count'), 1)

    def test_update_joint(self):
        url_detail = reverse.reverse('editors:procedure-joints-detail', [
            'test-procedure-2',
            'test-procedure-2-joint-1',
        ])
        response = self.client.patch(url_detail, data={
            'procedure': 'test-procedure-3',
            'signature': 'test-procedure-2-joint-0',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data.get('procedure'), 'test-procedure-3')
        self.assertEqual(
            response.data.get('signature'), 'test-procedure-2-joint-0')

    def test_retrieve_joint(self):
        url_detail = reverse.reverse('editors:procedure-joints-detail', [
            'test-procedure-2',
            'test-procedure-2-joint-1',
        ])
        response = self.client.get(url_detail)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data.get('procedure'), 'test-procedure-1')
        self.assertEqual(
            response.data.get('signature'), 'test-procedure-2-joint-1')

    def test_create_joint_input(self):
        url_list = reverse.reverse('editors:procedure-joint-inputs-list', [
            'test-procedure-2',
            'test-procedure-2-joint-1',
        ])
        response = self.client.post(url_list, data={
            'index': 1,
            'input_index': 0,
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('input_joint', response.data)
        self.assertEqual(response.data.get('index'), 1)
        self.assertEqual(response.data.get('input_index'), 0)
        self.assertEqual(response.data.get('input_joint'), None)

        response = self.client.post(url_list, data={
            'index': 2,
            'input_joint': 'test-procedure-2-joint-1',
            'input_index': 0,
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post(url_list, data={
            'index': 0,
            'input_index': 0,
        })
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    def test_destroy_joint_input(self):
        url_detail = reverse.reverse(
            'editors:procedure-joint-inputs-detail', [
                'test-procedure-2',
                'test-procedure-2-joint-1',
                0,
            ]
        )
        response = self.client.delete(url_detail)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_list_joint_input(self):
        url_list = reverse.reverse('editors:procedure-joint-inputs-list', [
            'test-procedure-2',
            'test-procedure-2-joint-1',
        ])
        response = self.client.get(url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count'), 1)


class ProcedureOutputTest(test.APITestCase):
    fixtures = [
        os.path.join('fixtures', 'test_editors.json')
    ]

    def test_create_output(self):
        url_list = reverse.reverse('editors:procedure-outputs-list', [
            'test-procedure-2',
        ])
        response = self.client.post(url_list, data={
            'signature': 'test-procedure-2-output-2',
            'index': 1,
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data.get('signature'), 'test-procedure-2-output-2')
        self.assertEqual(response.data.get('index'), 1)

    def test_destroy_output(self):
        url_detail = reverse.reverse('editors:procedure-outputs-detail', [
            'test-procedure-2', 0,
        ])
        response = self.client.delete(url_detail)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_list_output(self):
        url_list = reverse.reverse('editors:procedure-outputs-list', [
            'test-procedure-2',
        ])
        response = self.client.get(url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count'), 1)

    def test_update_output(self):
        url_detail = reverse.reverse('editors:procedure-outputs-detail', [
            'test-procedure-2', 0,
        ])
        response = self.client.patch(url_detail, data={
            'signature': 'test-procedure-2-output-3',
            'index': 3,
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data.get('signature'), 'test-procedure-2-output-3')
        self.assertEqual(response.data.get('index'), 3)

    def test_retrieve_output(self):
        url_detail = reverse.reverse('editors:procedure-outputs-detail', [
            'test-procedure-2', 0,
        ])
        response = self.client.get(url_detail)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data.get('signature'), 'test-procedure-2-output-1')
        self.assertEqual(response.data.get('index'), 0)
