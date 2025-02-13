from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time

MAX_WAIT = 10

class NewVisitorTest(LiveServerTestCase):

	def setUp(self):
		self.browser = webdriver.Firefox()

	def tearDown(self):
		self.browser.quit()

	# Auxiliary method 
	def wait_for_row_in_list_table(self, row_text):
		start_time = time.time()
		while True:
			try:
				table = self.browser.find_element(By.ID,'id_list_table')
				rows = table.find_elements(By.TAG_NAME, 'tr')
				self.assertIn(row_text, [row.text for row in rows])
				return
			except(AssertionError, WebDriverException) as e:
				if ((time.time() - start_time) > MAX_WAIT):
					raise e
				time.sleep(0.5)

	def test_a_navigation_buttons(self):
		self.browser.get(self.live_server_url)

		inputbox = self.browser.find_element(By.ID, 'id_new_item')
		inputbox.send_keys('Testar botões de navegação')
		inputbox.send_keys(Keys.ENTER)
		time.sleep(1)

		# Verifica se o botão "Anterior" está desabilitado na primeira lista
		previous_button = self.browser.find_element(By.ID, 'btn_anterior')
		self.assertTrue(previous_button.get_attribute('disabled'))

		# Verifica se o botão "Próximo" está habilitado
		next_button = self.browser.find_element(By.ID, 'btn_proximo')
		self.assertFalse(next_button.get_attribute('disabled'))

		# Cria uma nova lista para testar a navegação
		self.browser.get(self.live_server_url)
		time.sleep(1)

		inputbox = self.browser.find_element(By.ID, 'id_new_item')
		inputbox.send_keys('Testar botões de navegação lista 2')
		inputbox.send_keys(Keys.ENTER)
		time.sleep(1)

		# Verifica se o botão "Anterior" agora está habilitado
		previous_button = self.browser.find_element(By.ID, 'btn_anterior')
		self.assertFalse(previous_button.get_attribute('disabled'))

		# Clica no botão "Anterior" e verifica se voltou para a lista 1
		previous_button.click()
		self.assertEqual(self.browser.current_url, self.live_server_url + '/lists/1/')

		# Clica no botão "Próximo" para ir para a lista 2
		self.browser.get(self.live_server_url + '/lists/1/')
		next_button = self.browser.find_element(By.ID, 'btn_proximo')
		next_button.click()
		self.assertEqual(self.browser.current_url, self.live_server_url + '/lists/2/')
		
	def test_can_start_a_list_for_one_user(self):
		# Edith ouviu falar de uma nova aplicação online interessante
		# para lista de tarefas. Ela decide verificar a homepage

		self.browser.get(self.live_server_url)

		# Ela percebe que o título da página e o cabeçalho mencionam
		# listas de tarefas (to-do)

		self.assertIn('To-Do', self.browser.title)
		header_text = self.browser.find_element(By.TAG_NAME, 'h1').text
		self.assertIn('To-Do', header_text)
		
		# Ela é convidada a inserir um item de tarefa imediatamente

		inputbox = self.browser.find_element(By.ID, 'id_new_item')
		self.assertEqual(
			inputbox.get_attribute('placeholder'),
			'Enter a to-do item'
		)

		# Ela digita "Buy peacock feathers" (Comprar penas de pavão)
		# em uma nova caixa de texto (o hobby de Edith é fazer iscas
		# para pesca com fly)

		inputbox.send_keys('Buy peacock feathers')


		# Quando ela tecla enter, a página é atualizada, e agora
		# a página lista "1 - Buy peacock feathers" como um item em 
		# uma lista de tarefas

		inputbox.send_keys(Keys.ENTER)
		time.sleep(1)
		self.wait_for_row_in_list_table('1: Buy peacock feathers')

		# Ainda continua havendo uma caixa de texto convidando-a a 
		# acrescentar outro item. Ela insere "Use peacock feathers 
		# make a fly" (Usar penas de pavão para fazer um fly - 
		# Edith é bem metódica)
		inputbox = self.browser.find_element(By.ID,'id_new_item')
		inputbox.send_keys("Use peacock feathers to make a fly")
		inputbox.send_keys(Keys.ENTER)
		time.sleep(1)

		# A página é atualizada novamente e agora mostra os dois
		# itens em sua lista
		self.wait_for_row_in_list_table('1: Buy peacock feathers')
		self.wait_for_row_in_list_table('2: Use peacock feathers to make a fly')

		# Edith se pergunta se o site lembrará de sua lista. Então
		# ela nota que o site gerou um URL único para ela -- há um 
		# pequeno texto explicativo para isso.

		# Ela acessa essa URL -- sua lista de tarefas continua lá.

		# Satisfeita, ela volta a dormir

	def test_multiple_users_can_start_lists_at_different_urls(self):
		# Edith inicia uma nova lista de tarefas
		self.browser.get(self.live_server_url)
		inputbox = self.browser.find_element(By.ID, 'id_new_item')
		inputbox.send_keys('Buy peacock feathers')
		inputbox.send_keys(Keys.ENTER)
		self.wait_for_row_in_list_table('1: Buy peacock feathers')

		#Ela percebe que sua lista te um URL único
		edith_list_url = self.browser.current_url
		self.assertRegex(edith_list_url, '/lists/.+')

		#Agora um novo usuário, Francis, chega ao site

		## Usamos uma nova versão do nagegador para garantir que nenhuma 
		## informação de Edith está vindo de cookies, etc
		
		self.browser.quit()
		self.browser = webdriver.Firefox()

		# Francis acessa a página inicial. Não há sinal da lista de Edith
		self.browser.get(self.live_server_url)
		elements = self.browser.find_elements(By.TAG_NAME, 'body')
		page_text = " ".join(element.text for element in elements)		
		self.assertNotIn('Buy peacock feathers', page_text)
		self.assertNotIn('make a fly', page_text)
		
		# Francis inicia uma nova lista inserindo um novo item.
		inputbox = self.browser.find_element(By.ID, 'id_new_item')
		inputbox.send_keys('Buy milk')
		inputbox.send_keys(Keys.ENTER)
		self.wait_for_row_in_list_table('1: Buy milk')

		# Francis obtém seu próprio URL exclusivo
		francis_list_url = self.browser.current_url
		self.assertRegex(edith_list_url, '/lists/.+')
		self.assertNotEqual( francis_list_url, edith_list_url)

		# Novamente não há sinal algum da lista de Edith
		elements = self.browser.find_elements(By.TAG_NAME, 'body')
		page_text = " ".join(element.text for element in elements)
		self.assertNotIn('Buy peacock feathers', page_text)
		self.assertIn('Buy milk', page_text)