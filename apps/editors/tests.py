from mb_drf_extensions import test
from rest_framework import (
    reverse,
    status,
)

from ..scopes import scope_of_users

uuid_of_user = 'f0889553-0eef-11eb-b3e5-a87eea00b085'


class ProcedureSiteTest(test.APITestCase):
    fixtures = [
        'test_users.json',
        'test_editors.json',
    ]

    @test.authentication_mock(
        user_uuid=uuid_of_user,
        user_scopes=[scope_of_users]
    )
    def test_init_site(self):
        # init api will generate builtin site and procedures
        url_init = reverse.reverse('editors:sites-init')
        response = self.client.post(url_init)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # check if builtin site and procedures have been generated
        url_list = reverse.reverse('editors:procedures-list', ['builtin'])
        response = self.client.get(url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(response.data.get('count'), 0)

    @test.authentication_mock(
        access_token='BuiltinAccessToken',
    )
    def test_init_site_by_builtin_user(self):
        # init api will generate builtin site and procedures
        url_init = reverse.reverse('editors:sites-init')
        response = self.client.post(url_init)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @test.authentication_mock(
        user_uuid=uuid_of_user,
        user_scopes=[scope_of_users]
    )
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

    @test.authentication_mock(
        user_uuid=uuid_of_user,
        user_scopes=[scope_of_users]
    )
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

    @test.authentication_mock(
        user_uuid=uuid_of_user,
        user_scopes=[scope_of_users]
    )
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

    @test.authentication_mock(
        user_uuid=uuid_of_user,
        user_scopes=[scope_of_users]
    )
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

    @test.authentication_mock(
        user_uuid=uuid_of_user,
        user_scopes=[scope_of_users]
    )
    def test_list_sub_sites(self):
        url_base_sites = reverse.reverse(
            'editors:site-base-sites-list', ['test-site-3'])
        response = self.client.get(url_base_sites)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count'), 1)

    @test.authentication_mock(
        user_uuid=uuid_of_user,
        user_scopes=[scope_of_users]
    )
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
        'test_users.json',
        'test_editors.json',
    ]

    @test.authentication_mock(
        user_uuid=uuid_of_user,
        user_scopes=[scope_of_users]
    )
    def test_create_procedure(self):
        url_list = reverse.reverse('editors:procedures-list', ['test-site-1'])

        response = self.client.post(url_list, data={
            'signature': 'test-procedure',
            'docstring': 'test-procedure-doc',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('joints', response.data)
        self.assertIn('inputs', response.data)
        self.assertIn('outputs', response.data)
        self.assertEqual(response.data.get('signature'), 'test-procedure')
        self.assertEqual(response.data.get('docstring'), 'test-procedure-doc')

    @test.authentication_mock(
        user_uuid=uuid_of_user,
        user_scopes=[scope_of_users]
    )
    def test_destroy_procedure(self):
        url_detail_1 = reverse.reverse(
            'editors:procedures-detail', ['test-site-1', 'test-procedure-1'])
        response = self.client.delete(url_detail_1)
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

        url_detail_2 = reverse.reverse(
            'editors:procedures-detail', ['test-site-2', 'test-procedure-2'])
        response = self.client.delete(url_detail_2)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    @test.authentication_mock(
        user_uuid=uuid_of_user,
        user_scopes=[scope_of_users]
    )
    def test_list_procedure(self):
        url_list = reverse.reverse('editors:procedures-list', ['test-site-1'])
        response = self.client.get(url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count'), 2)

        response = self.client.get(
            url_list, QUERY_STRING='signature=test-procedure-1')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count'), 1)

    @test.authentication_mock(
        user_uuid=uuid_of_user,
        user_scopes=[scope_of_users]
    )
    def test_update_procedure(self):
        url_detail = reverse.reverse(
            'editors:procedures-detail', ['test-site-1', 'test-procedure-1'])
        response = self.client.patch(url_detail, data={
            'signature': 'test-procedure-1-1',
            'docstring': 'test-procedure-doc-1-1',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data.get('signature'), 'test-procedure-1-1')
        self.assertEqual(
            response.data.get('docstring'), 'test-procedure-doc-1-1')

    @test.authentication_mock(
        user_uuid=uuid_of_user,
        user_scopes=[scope_of_users]
    )
    def test_retrieve_procedure(self):
        url_detail = reverse.reverse(
            'editors:procedures-detail', ['test-site-1', 'test-procedure-1'])
        response = self.client.get(url_detail)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @test.authentication_mock(
        user_uuid=uuid_of_user,
        user_scopes=[scope_of_users]
    )
    def test_create_procedure_input(self):
        url_input_list = reverse.reverse(
            'editors:procedure-inputs-list',
            ['test-site-1', 'test-procedure-1']
        )
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

    @test.authentication_mock(
        user_uuid=uuid_of_user,
        user_scopes=[scope_of_users]
    )
    def test_destroy_procedure_input(self):
        url_input_detail = reverse.reverse(
            'editors:procedure-inputs-detail',
            ['test-site-1', 'test-procedure-1', 0]
        )
        response = self.client.delete(url_input_detail)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.delete(url_input_detail)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @test.authentication_mock(
        user_uuid=uuid_of_user,
        user_scopes=[scope_of_users]
    )
    def test_list_procedure_input(self):
        url_input_list = reverse.reverse(
            'editors:procedure-inputs-list',
            ['test-site-1', 'test-procedure-1']
        )
        response = self.client.get(url_input_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count'), 1)

    @test.authentication_mock(
        user_uuid=uuid_of_user,
        user_scopes=[scope_of_users]
    )
    def test_update_procedure_input(self):
        url_input_detail = reverse.reverse(
            'editors:procedure-inputs-detail',
            ['test-site-1', 'test-procedure-1', 0]
        )
        response = self.client.patch(url_input_detail, data={
            'index': 10,
            'signature': 'test-input-10',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('index'), 10)

        response = self.client.get(url_input_detail)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        url_input_detail = reverse.reverse(
            'editors:procedure-inputs-detail',
            ['test-site-1', 'test-procedure-1', 10])
        response = self.client.get(url_input_detail)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('index'), 10)


class ProcedureJointTest(test.APITestCase):
    fixtures = [
        'test_users.json',
        'test_editors.json',
    ]

    @test.authentication_mock(
        user_uuid=uuid_of_user,
        user_scopes=[scope_of_users]
    )
    def test_create_joint(self):
        url_list = reverse.reverse(
            'editors:procedure-joints-list',
            ['test-site-2', 'test-procedure-2']
        )
        response = self.client.post(url_list, data={
            'signature': 'test-joint-1',
            'site': 'test-site-1',
            'procedure': 'test-procedure-1',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post(url_list, data={
            'signature': 'test-joint-2',
            'procedure': 'test-procedure-2',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @test.authentication_mock(
        user_uuid=uuid_of_user,
        user_scopes=[scope_of_users]
    )
    def test_destroy_joint(self):
        url_detail = reverse.reverse('editors:procedure-joints-detail', [
            'test-site-2',
            'test-procedure-2',
            'test-procedure-2-joint-1',
        ])
        response = self.client.delete(url_detail)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    @test.authentication_mock(
        user_uuid=uuid_of_user,
        user_scopes=[scope_of_users]
    )
    def test_list_joint(self):
        url_list = reverse.reverse(
            'editors:procedure-joints-list',
            ['test-site-2', 'test-procedure-2'],
        )
        response = self.client.get(url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count'), 1)

    @test.authentication_mock(
        user_uuid=uuid_of_user,
        user_scopes=[scope_of_users]
    )
    def test_update_joint(self):
        url_detail = reverse.reverse('editors:procedure-joints-detail', [
            'test-site-2',
            'test-procedure-2',
            'test-procedure-2-joint-1',
        ])
        response = self.client.patch(url_detail, data={
            'procedure': 'test-procedure-3',
            'signature': 'test-procedure-2-joint-0',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(
            response.data.get('procedure'), 'test-procedure-3')
        self.assertEqual(
            response.data.get('signature'), 'test-procedure-2-joint-0')

    @test.authentication_mock(
        user_uuid=uuid_of_user,
        user_scopes=[scope_of_users]
    )
    def test_retrieve_joint(self):
        url_detail = reverse.reverse('editors:procedure-joints-detail', [
            'test-site-2',
            'test-procedure-2',
            'test-procedure-2-joint-1',
        ])
        response = self.client.get(url_detail)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data.get('procedure'), 'test-procedure-1')
        self.assertEqual(
            response.data.get('signature'), 'test-procedure-2-joint-1')

    @test.authentication_mock(
        user_uuid=uuid_of_user,
        user_scopes=[scope_of_users]
    )
    def test_create_joint_input(self):
        url_list = reverse.reverse('editors:procedure-joint-inputs-list', [
            'test-site-2',
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

    @test.authentication_mock(
        user_uuid=uuid_of_user,
        user_scopes=[scope_of_users]
    )
    def test_destroy_joint_input(self):
        url_detail = reverse.reverse(
            'editors:procedure-joint-inputs-detail',
            [
                'test-site-2',
                'test-procedure-2',
                'test-procedure-2-joint-1',
                0,
            ]
        )
        response = self.client.delete(url_detail)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    @test.authentication_mock(
        user_uuid=uuid_of_user,
        user_scopes=[scope_of_users]
    )
    def test_list_joint_input(self):
        url_list = reverse.reverse('editors:procedure-joint-inputs-list', [
            'test-site-2',
            'test-procedure-2',
            'test-procedure-2-joint-1',
        ])
        response = self.client.get(url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count'), 1)


class ProcedureOutputTest(test.APITestCase):
    fixtures = [
        'test_users.json',
        'test_editors.json',
    ]

    @test.authentication_mock(
        user_uuid=uuid_of_user,
        user_scopes=[scope_of_users]
    )
    def test_create_output(self):
        url_list = reverse.reverse('editors:procedure-outputs-list', [
            'test-site-2',
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

    @test.authentication_mock(
        user_uuid=uuid_of_user,
        user_scopes=[scope_of_users]
    )
    def test_destroy_output(self):
        url_detail = reverse.reverse('editors:procedure-outputs-detail', [
            'test-site-2',
            'test-procedure-2',
            0,
        ])
        response = self.client.delete(url_detail)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    @test.authentication_mock(
        user_uuid=uuid_of_user,
        user_scopes=[scope_of_users]
    )
    def test_list_output(self):
        url_list = reverse.reverse('editors:procedure-outputs-list', [
            'test-site-2',
            'test-procedure-2',
        ])
        response = self.client.get(url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count'), 1)

    @test.authentication_mock(
        user_uuid=uuid_of_user,
        user_scopes=[scope_of_users]
    )
    def test_update_output(self):
        url_detail = reverse.reverse('editors:procedure-outputs-detail', [
            'test-site-2',
            'test-procedure-2',
            0,
        ])
        response = self.client.patch(url_detail, data={
            'signature': 'test-procedure-2-output-3',
            'index': 3,
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data.get('signature'), 'test-procedure-2-output-3')
        self.assertEqual(response.data.get('index'), 3)

    @test.authentication_mock(
        user_uuid=uuid_of_user,
        user_scopes=[scope_of_users]
    )
    def test_retrieve_output(self):
        url_detail = reverse.reverse('editors:procedure-outputs-detail', [
            'test-site-2',
            'test-procedure-2',
            0,
        ])
        response = self.client.get(url_detail)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data.get('signature'), 'test-procedure-2-output-1')
        self.assertEqual(response.data.get('index'), 0)
